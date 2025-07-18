import shlex
from utils.display import print_info, print_error, print_story, print_location, prompt_input, print_responsibility_warning
from game.safety import VALID_LEVELS
import utils.file_handler as file_handler

def handle_command(user_action, game_state, story_manager, last_player_action):
    """
    Processes user commands, modifying the game state and handling game logic.
    Returns a tuple: (should_continue, last_player_action)
    """
    action_lower = user_action.lower().lstrip('/')
    
    if action_lower.startswith('save'):
        parts = action_lower.split(' ', 1)
        if len(parts) > 1 and parts[1]:
            save_name = parts[1]
            file_handler.save_game(game_state, save_name)
        else:
            print_error("Usage: /save <filename>")
        return True, last_player_action

    elif action_lower.startswith('safe '):
        parts = action_lower.split(' ', 1)
        if len(parts) > 1 and parts[1] in VALID_LEVELS:
            new_level = parts[1]
            if new_level == 'none' and game_state.safety_level != 'none':
                print_responsibility_warning()
                confirm = prompt_input("Are you sure you want to continue? (yes/no): ").lower()
                if confirm != 'yes':
                    print_info("Safety level change cancelled.")
                    return True, last_player_action
            
            game_state.safety_level = new_level
            print_info(f"Content safety level set to: {new_level.upper()}")
        else:
            print_error(f"Invalid safety level. Use one of: {', '.join(VALID_LEVELS)}")
        return True, last_player_action

    elif action_lower == 'revert':
        if game_state.revert_last_turn():
            print_info("Last turn reverted.")
            print_story("\n" + game_state.get_current_story())
        else:
            print_error("Nothing to revert.")
        return True, last_player_action

    elif action_lower == 'retry':
        if last_player_action and game_state.revert_last_turn():
            print_info("Re-running last action...")
            story_text, commands = story_manager.process_action(last_player_action)
            # This part needs to be handled in the main loop as it affects the story
            return "retry", last_player_action
        else:
            print_error("No previous action to retry.")
        return True, last_player_action

    elif action_lower == 'undo':
        if game_state.undo():
            print_info("Undo successful.")
            print_story("\n" + game_state.get_current_story())
        else:
            print_error("Cannot undo further.")
        return True, last_player_action

    elif action_lower == 'redo':
        if game_state.redo():
            print_info("Redo successful.")
            print_story("\n" + game_state.get_current_story())
        else:
            print_error("Cannot redo further.")
        return True, last_player_action

    elif action_lower == 'world' or action_lower.startswith('world '):
        parts = action_lower.split(' ', 1)
        if len(parts) > 1 and parts[1] == 'info':
            world = game_state.world
            print_info(f"\n--- World Info: {world.name} ---")
            print(f"Genre: {world.genre}")
            print(f"Description: {world.description}")
            
            if world.classes:
                print("\nAvailable Classes:")
                for c in world.classes.values():
                    print(f"- {c.name}: {c.description}")

            if world.races:
                print("\nAvailable Races:")
                for r in world.races.values():
                    print(f"- {r.name}: {r.description}")
            
            if world.factions:
                print("\nMajor Factions:")
                for f in world.factions.values():
                    print(f"- {f.name}: {f.description}")

            print_info("---------------------------------")
        else:
            print_error("Usage: /world info")
        return True, last_player_action

    elif action_lower.startswith('memory '):
        parts = action_lower.split(' ', 2)
        if len(parts) > 1:
            sub_cmd = parts[1]
            if sub_cmd == 'add' and len(parts) > 2:
                fact = parts[2]
                game_state.memory_manager.add_to_memory_bank(fact)
                print_info(f"Noted: '{fact}'")
            elif sub_cmd == 'show':
                print_info("\n--- Memory Bank ---")
                if game_state.memory_manager.memory_bank:
                    for i, fact in enumerate(game_state.memory_manager.memory_bank):
                        print(f"{i+1}: {fact.fact}")
                else:
                    print("The memory bank is empty.")
                print_info("-------------------")
            else:
                print_error("Usage: /memory [add <fact>|show]")
        else:
            print_error("Usage: /memory [add <fact>|show]")
        return True, last_player_action

    elif action_lower.startswith('card '):
        try:
            parts = shlex.split(user_action)
            if len(parts) > 1:
                sub_cmd = parts[1].lower()
                if sub_cmd == 'create':
                    try:
                        # Find the --triggers flag
                        trigger_index = parts.index('--triggers')
                        # Name is the second argument
                        name = parts[2]
                        # Entry is everything between the name and --triggers
                        entry = " ".join(parts[3:trigger_index])
                        # Triggers are everything after --triggers
                        triggers_list = parts[trigger_index+1:]
                        
                        if not name or not entry or not triggers_list:
                            raise ValueError

                        triggers_dict = {t: 1.0 for t in triggers_list}
                        card = game_state.memory_manager.create_story_card(name, entry, triggers_dict)
                        print_info(f"Created Story Card: '{card.name}'")

                    except (ValueError, IndexError):
                        print_error('Usage: /card create <name> "<entry>" --triggers <trigger1> "<trigger 2>" ...')

                elif sub_cmd == 'list':
                    print_info("\n--- Story Cards ---")
                    if game_state.memory_manager.story_cards:
                        for card in game_state.memory_manager.story_cards.values():
                            print(f"- {card.name}: triggers on [{', '.join(card.triggers.keys())}]")
                    else:
                        print("No story cards have been created.")
                    print_info("-------------------")
                else:
                    print_error("Usage: /card [create <details>|list]")
            else:
                print_error("Usage: /card [create <details>|list]")
        except Exception as e:
            print_error(f"An error occurred parsing the card command: {e}")
        return True, last_player_action

    elif action_lower in ['quit', 'quit']:
        print_info("Thank you for playing StoryForge!")
        return "quit", last_player_action

    elif action_lower == 'stats':
        print_info("\n--- API Usage Statistics ---")
        print_info(f"Total API Calls: {game_state.api_calls}")
        print_info(f"Total Input Tokens: {game_state.total_input_tokens}")
        print_info(f"Total Output Tokens: {game_state.total_output_tokens}")
        print_info("----------------------------")
        return True, last_player_action

    return False, last_player_action