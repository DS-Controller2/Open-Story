from colorama import Fore, Style, Back
import sys
import time
import threading
from markdown_it import MarkdownIt
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PromptToolkitStyle

# --- Core Markdown to ANSI Conversion (Reworked) ---

def _markdown_to_ansi(text: str, base_color=Fore.CYAN) -> str:
    """
    Converts a subset of Markdown to ANSI escape codes for terminal display.
    This version correctly handles nested inline styles.
    """
    md = MarkdownIt()
    tokens = md.parse(text)
    ansi_text = ""

    for token in tokens:
        # Block-level tokens
        if token.type == "paragraph_open":
            pass  # Spacing is handled by paragraph_close
        elif token.type == "paragraph_close":
            ansi_text += "\n"
        elif token.type == "bullet_list_open":
            pass  # Spacing handled by list items
        elif token.type == "list_item_open":
            ansi_text += "  * "
        elif token.type == "list_item_close":
            pass # The paragraph inside the list item adds the newline
        elif token.type == "fence":
            # For fenced code, use the draw_box utility for a clean look
            lang = f"({token.info})" if token.info else ""
            code_text = token.content.strip()
            # Use a distinct, self-contained style for code blocks
            ansi_text += draw_box(f"{lang}\n{code_text}", color=Fore.YELLOW) + "\n"
        # Inline content token (contains text and formatting)
        elif token.type == "inline":
            for child in token.children:
                if child.type == "strong_open":
                    ansi_text += Style.BRIGHT
                elif child.type == "strong_close":
                    ansi_text += Style.NORMAL
                elif child.type == "em_open":
                    # Style.ITALIC is not well-supported; Style.DIM is a good alternative
                    ansi_text += Style.DIM
                elif child.type == "em_close":
                    ansi_text += Style.NORMAL
                elif child.type == "code_inline":
                    # Switch to a code color, then revert to the base color
                    ansi_text += f"{Fore.LIGHTYELLOW_EX}{child.content}{base_color}"
                elif child.type == "text":
                    ansi_text += child.content
                elif child.type == "softbreak":
                    ansi_text += "\n"

    # Start with base color and clean up extraneous whitespace
    return (base_color + ansi_text.strip()).strip()

# --- Loading Animation (Re-implemented as a Context Manager) ---

class _LoadingSpinner:
    """A thread-safe context manager to show a spinner animation."""

    def __init__(self, message: str = "Thinking...", delay: float = 0.1):
        self.message = message
        self.delay = delay
        self.spinner = ["-", "\\", "|", "/"]
        self.running = False
        self.spinner_thread = None

    def _spin(self):
        idx = 0
        while self.running:
            # Use \r to return to the start of the line and overwrite
            spinner_char = self.spinner[idx % len(self.spinner)]
            output = f"\r{Fore.BLUE}{self.message} {spinner_char}{Style.RESET_ALL}"
            sys.stdout.write(output)
            sys.stdout.flush()
            time.sleep(self.delay)
            idx += 1

    def __enter__(self):
        self.running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        # Clear the line
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
        sys.stdout.flush()


def print_loading(message="Thinking..."):
    """
    Returns a context manager that displays a loading animation.
    Usage:
        with print_loading("Working..."):
            time.sleep(3) # Your long-running task here
    """
    return _LoadingSpinner(message)


# --- UI and Helper Functions (with fixes and improvements) ---

def draw_box(text: str, color=Fore.WHITE) -> str:
    """Draws a correctly formatted box around the given text."""
    lines = text.split('\n')
    # Calculate max_len based on content, not including padding
    max_len = max(len(line) for line in lines) if lines else 0

    # The width of the box content, including 1-char padding on each side
    content_width = max_len + 2

    # Top/bottom border
    top_bottom = "+" + "-" * content_width + "+"

    # Build the list of lines to be joined
    boxed_lines = [top_bottom]
    for line in lines:
        # Pad the line with spaces to align with the box width
        padded_line = f" {line.ljust(max_len)} "
        boxed_lines.append(f"|{padded_line}|")
    boxed_lines.append(top_bottom)

    # Join lines and apply color to the whole block for efficiency
    return color + "\n".join(boxed_lines) + Style.RESET_ALL

def print_story(text: str):
    """Prints the main story text in a standard color, with markdown support."""
    # Delegate color and style handling to the markdown parser
    ansi_formatted_text = _markdown_to_ansi(text, base_color=Fore.LIGHTWHITE_EX + Style.BRIGHT)
    print("\n" + ansi_formatted_text + Style.RESET_ALL)

def print_info(text: str):
    """Prints informational text (e.g., save confirmations, help) in a bright color."""
    print(Fore.LIGHTWHITE_EX + text + Style.RESET_ALL)

def print_error(text: str):
    """Prints error messages."""
    print(Fore.RED + text + Style.RESET_ALL)

def print_game_over(text: str):
    """Prints the game over message in a dramatic style."""
    print(Fore.RED + Back.WHITE + Style.BRIGHT + text + Style.RESET_ALL)

def print_location(text: str):
    """Prints location descriptions in a distinct color."""
    print(Fore.CYAN + text + Style.RESET_ALL)

def print_exits(text: str):
    """Prints the list of available exits."""
    print(Fore.LIGHTMAGENTA_EX + text + Style.RESET_ALL)

def print_player_status(status_string: str):
    """Prints the player's formatted status."""
    print(Fore.GREEN + status_string + Style.RESET_ALL)

def prompt_input(prompt_text: str = "What do you do? > ", style=None) -> str:
    """Displays the input prompt using prompt_toolkit and gets user input."""
    if style is None:
        style = PromptToolkitStyle.from_dict({
            'prompt': 'ansiyellow',
        })
    session = PromptSession(style=style)
    user_input = session.prompt(prompt_text)
    print(f"{Fore.YELLOW}>>> Your Action: {user_input}{Style.RESET_ALL}")
    return user_input


def print_responsibility_warning():
    """Prints a clear, one-time warning when switching to the 'none' safety level."""
    border = Fore.RED + Style.BRIGHT + "================================ WARNING ================================" + Style.RESET_ALL
    message_text = (
        "You have set the content safety level to 'NONE'.\n"
        "You are solely responsible for all prompts and generated content.\n"
        "The narrative may now include mature or disturbing themes.\n"
        "Proceed with caution."
    )
    message = f"{Fore.YELLOW}{message_text}{Style.RESET_ALL}"
    print(f"\n{border}\n{message}\n{border}\n")
