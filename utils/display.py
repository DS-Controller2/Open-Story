from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.style import Style
from rich.table import Table
from rich.text import Text

console = Console()

def print_story(text: str):
    """Prints the main story text in a standard color, with markdown support."""
    console.print(Panel(Markdown(text), title="Story", style="bold white", border_style="bright_white"))

def print_info(text: str):
    """Prints informational text (e.g., save confirmations, help) in a bright color."""
    console.print(Text(text, style="bright_white"))

def print_error(text: str):
    """Prints error messages."""
    console.print(Panel(Text(text, style="bold red"), title="Error"))

def print_game_over(text: str):
    """Prints the game over message in a dramatic style."""
    console.print(Panel(Text(text, style="bold white on red"), title="Game Over"))

def print_location(text: str):
    """Prints location descriptions in a distinct color."""
    console.print(Panel(Markdown(text), title="Location", style="cyan", border_style="cyan"))

def print_exits(text: str):
    """Prints the list of available exits."""
    console.print(Text(f"Exits: {text}", style="magenta"))

def print_player_status(status_string: str):
    """Prints the player's formatted status."""
    console.print(Panel(Text(status_string), title="Player Status", style="green", border_style="green"))

def prompt_input(prompt_text: str = "What do you do? > ") -> str:
    """Displays the input prompt using prompt_toolkit and gets user input."""
    user_input = Prompt.ask(f"[bold yellow]{prompt_text}[/bold yellow]")
    console.print(f"[bold yellow]>>> Your Action: {user_input}[/bold yellow]")
    return user_input

def print_responsibility_warning():
    """Prints a clear, one-time warning when switching to the 'none' safety level."""
    console.print(Panel(
        Text(
            "You have set the content safety level to 'NONE'.\n"
            "You are solely responsible for all prompts and generated content.\n"
            "The narrative may now include mature or disturbing themes.\n"
            "Proceed with caution.",
            style="yellow"
        ),
        title="Warning",
        border_style="bold red"
    ))
