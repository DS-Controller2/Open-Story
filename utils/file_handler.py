import os
import json
from game.game_state import GameState
from .display import print_info, print_error

SAVE_DIRECTORY = "saves"

def save_game(game_state: GameState, filename: str):
    """Saves the entire GameState object to a file using JSON."""
    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)
        
    filepath = os.path.join(SAVE_DIRECTORY, f"{filename}.json")
    try:
        with open(filepath, "w") as f:
            json.dump(game_state.to_dict(), f, indent=4)
        print_info(f"\nGame saved successfully to {filepath}")
        return True
    except Exception as e:
        print_error(f"\nError saving game: {e}")
        return False

def load_game(filename: str):
    """Loads a GameState object from a file. Returns GameState or None."""
    filepath = os.path.join(SAVE_DIRECTORY, f"{filename}.json")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            game_state = GameState.from_dict(data)
        print_info(f"\nGame loaded successfully from {filepath}")
        return game_state
    except FileNotFoundError:
        print_error(f"\nSave file not found: {filepath}")
        return None
    except Exception as e:
        print_error(f"\nError loading game: {e}")
        return None

def list_save_files():
    """Lists all available save files."""
    if not os.path.exists(SAVE_DIRECTORY):
        return []
    
    files = os.listdir(SAVE_DIRECTORY)
    save_files = [f.replace(".json", "") for f in files if f.endswith(".json")]
    return save_files
