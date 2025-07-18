import os
import pickle
from game.game_state import GameState
from .display import print_info, print_error

SAVE_DIRECTORY = "saves"

def save_game(game_state: GameState, filename: str):
    """Saves the entire GameState object to a file using pickle."""
    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)
        
    filepath = os.path.join(SAVE_DIRECTORY, f"{filename}.sav")
    try:
        with open(filepath, "wb") as f:
            pickle.dump(game_state, f)
        print_info(f"\nGame saved successfully to {filepath}")
        return True
    except Exception as e:
        print_error(f"\nError saving game: {e}")
        return False

def load_game(filename: str):
    """Loads a GameState object from a file. Returns GameState or None."""
    filepath = os.path.join(SAVE_DIRECTORY, f"{filename}.sav")
    try:
        with open(filepath, "rb") as f:
            game_state = pickle.load(f)
        print_info(f"\nGame loaded successfully from {filepath}")
        return game_state
    except FileNotFoundError:
        print_error(f"\nSave file not found: {filepath}")
        return None
    except Exception as e:
        print_error(f"\nError loading game: {e}")
        return None