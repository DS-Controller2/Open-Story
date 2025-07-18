"""
This file centrally defines all slash-commands in the game.
The structure is a dictionary where each key is the command name,
and the value is another dictionary containing its properties:
- 'args': A list of valid arguments for completion and validation.
- 'help': A description of what the command does.
"""

COMMANDS = {
    "card": {
        "args": ["create", "list"],
        "help": "Manage story cards for conditional memory."
    },
    "help": {
        "args": [],
        "help": "Shows the help menu."
    },
    "load": {
        "args": [],
        "help": "Loads the game state from a file."
    },
    "memory": {
        "args": ["add", "show"],
        "help": "Manage the AI's long-term memory bank."
    },
    "quit": {
        "args": [],
        "help": "Exit the game."
    },
    "redo": {
        "args": [],
        "help": "Redo the last undone game state change."
    },
    "revert": {
        "args": [],
        "help": "Undo your last action and the AI's response."
    },
    "retry": {
        "args": [],
        "help": "Reroll the AI's last response from your previous action."
    },
    "safe": {
        "args": ["high", "mid", "low", "none"],
        "help": "Change the content safety level."
    },
    "save": {
        "args": [],
        "help": "Saves the current game state to a file."
    },
    "stats": {
        "args": [],
        "help": "Display API usage and token statistics."
    },
    "undo": {
        "args": [],
        "help": "Undo the last game state change."
    },
    "world": {
        "args": ["info"],
        "help": "Display information about the current world."
    }
}