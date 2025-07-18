# StoryForge

StoryForge is an interactive text-based adventure game powered by AI, acting as a dynamic Dungeon Master.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-repo/StoryForge.git
    cd StoryForge
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Copy the `.env.template` file to `.env` and fill in your API keys or other necessary configurations.
    ```bash
    cp .env.template .env
    # Open .env and add your GEMINI_API_KEY or other variables
    ```

## Running the Game

To start the game, run the `main.py` script:

```bash
python main.py
```

## Project Structure

-   `main.py`: The main entry point of the game.
-   `game/`: Contains core game logic, story management, player state, and AI interaction.
-   `utils/`: Utility functions for command handling, display, and file operations.
-   `saves/`: Directory for game save files.
-   `docs/`: Project documentation.
-   `tests/`: Unit tests for various modules.

