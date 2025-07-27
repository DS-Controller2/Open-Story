import os
print("Starting main.py")
from dotenv import load_dotenv
from colorama import init as colorama_init

# --- New Imports for Advanced Commands ---
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style as PromptToolkitStyle # Renamed to avoid conflict

from game.game_state import GameState
from game.story_manager import StoryManager
from game.world_db import create_custom_world
import utils.file_handler as file_handler
from utils.display import *
from utils.commands import COMMANDS # Import our new command definitions
from utils.command_handler import handle_command
from game.safety import VALID_LEVELS
from game.rate_limits import VALID_TIERS

import random # Needed for dice rolls

# --- Initialize Libraries ---
colorama_init()
load_dotenv()

# --- Custom Completer for prompt_toolkit ---
class GameCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split(' ')

        # --- Completion for main commands ---
        if len(words) == 1 and (text.startswith('/') or text.startswith('//')):
            prefix = '//' if text.startswith('//') else '/'
            command_text = text.lstrip('/')
            for cmd_name in sorted(COMMANDS.keys()):
                if cmd_name.startswith(command_text):
                    yield Completion(f"{prefix}{cmd_name}", start_position=-len(text), display_meta=COMMANDS[cmd_name]['help'])
            return

        # --- Completion for command arguments (sub-commands) ---
        if len(words) == 2 and (words[0].startswith('/') or words[0].startswith('//')):
            cmd = words[0].lstrip('/')
            if cmd in COMMANDS:
                arg_list = COMMANDS[cmd].get('args', [])
                for arg in arg_list:
                    if arg.startswith(words[1]):
                        yield Completion(arg, start_position=-len(words[1]))

# --- Helper Functions ---
def print_command_list():
    """Prints available slash commands, triggered by typing just '/'."""
    print_info("\n--- Available Commands ---")
    for cmd, details in sorted(COMMANDS.items()):
        print(f"  /{cmd:<15} {details['help']}")
    print_info("--------------------------")

def print_help_menu():
    print_info("\n--- Help ---")
    print_story("Story Actions: Type anything you want to do (e.g., 'look at the figure').")
    print_info("Utility Commands:")
    print("  'help', 'look', 'go <exit>', 'status', 'save <name>', 'quit'")
    print("  Type '/' and press Enter to see all advanced commands.")
    print_info("--------------------------")

def resolve_stat_check(player, stat, difficulty):
    """Rolls a d20, adds modifier, and checks against difficulty."""
    modifier = player.get_attribute_modifier(stat)
    roll = random.randint(1, 20)
    total = roll + modifier
    success = total >= difficulty
    
    result_text = f"[Stat Check: {stat}] You {'succeeded' if success else 'failed'}. (Roll: {roll} + Mod: {modifier} = {total} vs DC: {difficulty})"
    system_feedback = f"[SYSTEM: The player {'SUCCEEDED' if success else 'FAILED'} the {stat} check. Describe the outcome.]"
    
    return success, result_text, system_feedback

def apply_commands(game_state, commands):
    """Applies simple commands like HEALTH, ITEM, LOCATION."""
    if 'HEALTH' in commands:
        try:
            game_state.player.health += int(commands['HEALTH'])
        except (ValueError, TypeError):
            print_error(f"Invalid health value received from AI: {commands['HEALTH']}")
    if 'ITEM' in commands:
        item_cmd = commands['ITEM']
        if item_cmd.startswith('+') and len(item_cmd) > 1:
            try:
                item_name, item_weight_str = item_cmd[1:].split(',')
                item_weight = int(item_weight_str)
                if game_state.player.get_inventory_weight() + item_weight > game_state.player.max_inventory_weight:
                    print_error("You can't carry any more weight.")
                else:
                    game_state.player.inventory.append({"name": item_name, "weight": item_weight})
            except ValueError:
                print_error(f"Invalid item format received from AI: {item_cmd}")
        elif item_cmd.startswith('-') and len(item_cmd) > 1:
            item_name_to_remove = item_cmd[1:]
            for item in game_state.player.inventory:
                if item["name"] == item_name_to_remove:
                    game_state.player.inventory.remove(item)
                    break
    if 'LOCATION' in commands:
        location_key = commands['LOCATION']
        if game_state.world.get_location(location_key):
            game_state.current_location_key = location_key
        else:
            print_error(f"AI tried to move to an invalid location: {location_key}")

# --- Main Game Logic ---
def main():
    game_state = None
    print_info("Welcome to StoryForge!")
    print_info("Tip: For the best experience, run in a fullscreen terminal.")
    
    # Ask for API tier at the beginning
    api_tier_choice = ""
    while api_tier_choice not in VALID_TIERS:
        api_tier_choice = prompt_input(f"Choose your API tier ({'/'.join(VALID_TIERS)}): ").lower()
        if api_tier_choice not in VALID_TIERS:
            print_error("Invalid API tier. Please choose from the available options.")
    
    print_info(f"API tier set to: {api_tier_choice.upper()}")
    
    choice = prompt_input("Type 'new' to start a new adventure or 'load' to continue: ").lower()

    if choice == 'load':
        saves = file_handler.list_save_files()
        if not saves:
            print_error("No save files found.")
            game_state = None
        else:
            print_info("Available saves: " + ", ".join(saves))
            save_name = prompt_input("Enter the name of the save file to load: ")
            game_state = file_handler.load_game(save_name)
    
    if game_state is None:
        if choice == 'load': 
            print_info("Starting a new game instead.")
        game_state = GameState(api_tier=api_tier_choice)
        
        world_choice = ""
        while world_choice not in ['custom', 'default']:
            world_choice = prompt_input("Create a 'custom' world or use the 'default' world?: ").lower()
            if world_choice not in ['custom', 'default']:
                print_error("Invalid choice. Please type 'custom' or 'default'.")

        if world_choice == 'custom':
            game_state.world = create_custom_world(print_info, print_error)

        print_info(f"\n--- Welcome to {game_state.world.name} ---")
        print_story(game_state.world.description)
        
        player_name = prompt_input("\nEnter your hero's name: ")
        if player_name: game_state.player.name = player_name

        char_choice = ""
        while char_choice not in ['custom', 'preset']:
            char_choice = prompt_input("Choose character creation: 'custom' or 'preset': ").lower()
            if char_choice not in ['custom', 'preset']:
                print_error("Invalid choice. Please type 'custom' or 'preset'.")

        if char_choice == 'preset':
            available_classes = game_state.world.classes
            class_name = ""
            while class_name not in available_classes:
                class_name = prompt_input(f"Enter class name ({', '.join(available_classes.keys())}): ").lower()
                if class_name not in available_classes:
                    print_error("Invalid class name.")
            
            chosen_class = available_classes[class_name]
            for stat, points in chosen_class.attributes.items():
                game_state.player.attributes[stat] += points
            print_info(f"\n{chosen_class.name} preset applied!")
        
        elif char_choice == 'custom':
            print_info("\nCreate your character. You have 15 points to add to your base stats.")
            print_info("All stats start at 10. Assign points using the format 'STAT #', e.g., 'str 3'.")

            points_to_spend = 15
            valid_stats = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

            while points_to_spend > 0:
                print_info(f"\nPoints remaining: {points_to_spend}")
                current_stats_str = " | ".join([f"{stat}: {game_state.player.attributes[stat]}" for stat in valid_stats])
                print(current_stats_str)
                
                command = prompt_input("> ").upper()
                
                try:
                    parts = command.split()
                    if len(parts) != 2:
                        print_error("Invalid format. Please use 'STAT #', e.g., 'DEX 3'")
                        continue
                    stat_to_add = parts[0]
                    points_to_add = int(parts[1])
                    if stat_to_add not in valid_stats:
                        print_error(f"Invalid stat. Use one of: {', '.join(valid_stats)}")
                        continue
                    if points_to_add <= 0:
                        print_error("You must assign a positive number of points.")
                        continue
                    if points_to_add > points_to_spend:
                        print_error(f"You only have {points_to_spend} points remaining.")
                        continue
                    game_state.player.attributes[stat_to_add] += points_to_add
                    points_to_spend -= points_to_add
                except ValueError:
                    print_error("Invalid number. The second part must be a whole number.")
                except Exception as e:
                    print_error(f"An unexpected error occurred: {e}")

        print_info("\nCharacter creation complete!")
        game_state.player.health = game_state.player.calculate_max_health()
        print_player_status(game_state.player.display_status())

        story_manager = StoryManager(game_state)
        story_manager.start_story()
        current_story_text = game_state.get_current_story()
    else: # This handles a loaded game
        story_manager = StoryManager(game_state)
        print_info("\n--- Story Continues ---")
        current_story_text = game_state.get_current_story()

    print_story("\n" + current_story_text)

    style = PromptToolkitStyle.from_dict({'prompt': 'ansiwhite'})
    session = PromptSession(completer=GameCompleter(), style=style)
    last_player_action = None

    while True:
        file_handler.save_game(game_state, "autosave")
        game_state._save_snapshot()
        print_player_status("\n" + game_state.player.display_status())
        if game_state.player.health <= 0:
            print_game_over("\nYour health is zero. You have fallen.\n--- GAME OVER ---")
            break

        try:
            user_action = session.prompt()
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

        if not user_action:
            continue
        
        action_lower = user_action.lower()

        if action_lower.startswith('/') or action_lower.startswith('//'):
            command_result, last_player_action = handle_command(user_action, game_state, story_manager, last_player_action)
            if command_result == "quit":
                break
            elif command_result == "retry":
                story_text, commands = story_manager.process_action(last_player_action)
                apply_commands(game_state, commands)
                if story_text:
                    print_story("\n" + story_text)
                if 'CHECK' in commands:
                    stat, difficulty = commands['CHECK']
                    success, result_text, system_feedback = resolve_stat_check(game_state.player, stat, difficulty)
                    print_info(result_text)
                    consequence_text, final_commands = story_manager.process_action(system_feedback)
                    apply_commands(game_state, final_commands)
                    if consequence_text:
                        print_story("\n" + consequence_text)
            continue
        
        elif action_lower == 'help':
            print_help_menu()
            continue
        
        elif action_lower.startswith('go '):
            direction = action_lower.split(' ', 1)[1]
            exits = game_state.get_current_location_exits()
            if direction in exits:
                game_state.current_location_key = exits[direction]
                print_info(f"\nYou go {direction}...")
                game_state.add_to_story(f"Moved to a new location.")
                print_location("\n" + game_state.get_current_location_description())
            else:
                print_error("You can't go that way.")
            continue
        
        else:
            last_player_action = user_action
            story_text, commands = story_manager.process_action(user_action)
            apply_commands(game_state, commands)
            
            if story_text:
                print_story("\n" + story_text)

            if 'CHECK' in commands:
                try:
                    stat, difficulty_str = commands['CHECK']
                    difficulty = int(difficulty_str)
                    success, result_text, system_feedback = resolve_stat_check(game_state.player, stat, difficulty)
                    print_info(result_text)
                    consequence_text, final_commands = story_manager.process_action(system_feedback)
                    apply_commands(game_state, final_commands)
                    if consequence_text:
                        print_story("\n" + consequence_text)
                except (ValueError, TypeError) as e:
                    print_error(f"Invalid stat check format from AI: CHECK {commands['CHECK']}. Error: {e}")
                except Exception as e:
                    print_error(f"An unexpected error occurred during stat check: {e}")

if __name__ == "__main__":
    main()