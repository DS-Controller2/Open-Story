import os
import re
import google.generativeai as genai

from .game_state import GameState
from .safety import get_safety_settings
from .prompts import get_system_prompt
from .rate_limits import get_rate_limits

# --- Constants for Context Management ---
# Set a practical limit for the model, e.g., Gemini 1.5 Flash has 1M, but we'll use a smaller portion.
MODEL_TOKEN_LIMIT = 8000 
CONTEXT_HISTORY_TARGET_PERCENT = 0.50 # Try to fill 50% of the remaining context with story history
CONTEXT_MEMORY_TARGET_PERCENT = 0.25  # And 25% with memory bank
CONTEXT_CARDS_TARGET_PERCENT = 0.25   # And 25% with story cards

class StoryManager:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.model = None
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("WARN: GEMINI_API_KEY environment variable not found.")
                return
            genai.configure(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash-latest")
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            print(f"Error during Gemini initialization: {e}")

    def start_story(self):
        if not self.game_state.story_history:
            location_desc = self.game_state.get_current_location_description()
            initial_text = (f"You are {self.game_state.player.name}, an adventurer. You find yourself in {location_desc} "
                            f"What do you do?")
            self.game_state.add_to_story(initial_text)

    def _parse_ai_response(self, response_text: str):
        clean_text = response_text
        commands = {}
        command_pattern = r'\[(HEALTH|ITEM|LOCATION|CHECK):\s*([^\]]+)\]'
        found_commands = re.findall(command_pattern, response_text)
        for key, value in found_commands:
            value = value.strip()
            if key == "CHECK":
                parts = value.split()
                if len(parts) == 2:
                    commands['CHECK'] = (parts[0].upper(), int(parts[1]))
            else:
                commands[key] = value
        clean_text = re.sub(command_pattern, '', clean_text).strip()
        return clean_text, commands

    def _build_context(self, player_action: str) -> str:
        """
        Assembles the full context to be sent to the AI, respecting token limits.
        """
        # 1. Essential, non-negotiable context
        world = self.game_state.world
        system_prompt = get_system_prompt(self.game_state.safety_level)
        rules_prompt = "--- RULE: STAT CHECKS ---\n[...]".replace("\\n", "\n") # Abridged for brevity
        player_status = self.game_state.player.display_status()
        location = self.game_state.get_current_location_object()

        # --- FAILSAFE ---
        if location is None:
            print_error("Error: Current location is invalid. The player is lost.")
            # Attempt to recover by moving to the starting location
            start_key = list(world.locations.keys())[0]
            self.game_state.current_location_key = start_key
            location = self.game_state.get_current_location_object()
            print_info(f"Returning to {location.name} to reorient.")
        
        base_context_list = [
            f"--- WORLD: {world.name} ({world.genre}) ---",
            world.description,
            system_prompt,
            rules_prompt,
            f"--- CURRENT LOCATION: {location.name} ---",
            location.description,
            f"--- PLAYER STATUS ---\n{player_status}"
        ]
        
        # Calculate remaining token budget
        base_context_str = "\n".join(base_context_list)
        base_token_count = self.model.count_tokens(base_context_str).total_tokens
        remaining_tokens = MODEL_TOKEN_LIMIT - base_token_count

        # 2. Dynamic context (Memories, Cards, History)
        # Get all potential dynamic content
        memory_bank = self.game_state.memory_manager.memory_bank
        recent_history = self.game_state.story_history
        
        # Combine story cards and world info entries
        active_story_cards = self.game_state.memory_manager.get_active_cards("\n".join(recent_history[-3:]))
        # For now, we assume all world info is relevant. This could be improved with triggers.
        active_world_info = world.world_info
        
        all_reminders = [f"Player Note: {c[0].entry}" for c in active_story_cards]
        all_reminders += [f"World Lore: {wi.entry}" for wi in active_world_info]

        # Allocate budgets
        history_budget = int(remaining_tokens * CONTEXT_HISTORY_TARGET_PERCENT)
        memory_budget = int(remaining_tokens * CONTEXT_MEMORY_TARGET_PERCENT)
        cards_budget = int(remaining_tokens * CONTEXT_CARDS_TARGET_PERCENT)

        # Fill context according to budget
        final_context = list(base_context_list)
        
        # Fill Story Cards & World Info
        if all_reminders:
            card_str = "\n".join(all_reminders)
            if self.model.count_tokens(card_str).total_tokens > cards_budget:
                print("WARN: Active reminders exceed budget. Truncating.")
            final_context.append(f"--- REMINDERS & LORE ---\n{card_str}")

        # Fill Memory Bank
        if memory_bank:
            memory_str = "\n".join([fact.fact for fact in memory_bank])
            if self.model.count_tokens(memory_str).total_tokens > memory_budget:
                print("WARN: Memory bank exceeds budget. Truncating.")
            final_context.append(f"--- MEMORY BANK ---\n{memory_str}")

        # Fill History (most recent first)
        if recent_history:
            history_str = "\n".join(recent_history[-3:])
            if self.model.count_tokens(history_str).total_tokens > history_budget:
                print("WARN: Recent history exceeds budget. Truncating.")
                # This is a simple truncation, a more sophisticated approach might be needed
                history_str = history_str[:history_budget]

            if history_str:
                final_context.append(f"--- RECENT STORY ---\n{history_str}")

        # Add player's immediate goal if it exists
        if self.game_state.player.goal:
            final_context.append(f"--- PLAYER'S GOAL ---\n{self.game_state.player.goal}")

        # 3. The latest action
        final_context.append(f"--- PLAYER'S ACTION ---\n> {player_action}")
        final_context.append("--- WHAT HAPPENS NEXT? (Narrative and optional commands) ---")
        
        return "\n\n".join(final_context)

    def process_action(self, action: str):
        if not self.model:
            return "The storyteller is silent. (Reason: AI not configured.)", {}

        full_prompt = self._build_context(action)
        
        settings = get_safety_settings(self.game_state.safety_level)
        tier_limits = get_rate_limits(self.game_state.api_tier)
        generation_config = {"max_output_tokens": 200}

        try:
            response = self.model.generate_content(
                contents=[full_prompt],
                generation_config=generation_config,
                safety_settings=settings
            )

            self.game_state.api_calls += 1
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                print(f"Usage metadata: {usage}")
                cached_tokens = getattr(usage, 'cached_content_token_count', 0)
                if cached_tokens > 0:
                    print(f"Context Caching: Active (Saved {cached_tokens} tokens)")
                else:
                    print("Context Caching: Inactive")
                self.game_state.total_input_tokens += usage.prompt_token_count
                self.game_state.total_output_tokens += usage.candidates_token_count
            
            clean_text, commands = self._parse_ai_response(response.text)
            self.game_state.add_to_story(f"> {action}\n\n{clean_text}")
            
            return clean_text, commands

        except Exception as e:
            return f"The storyteller hesitates... (An error occurred: {e})", {}
