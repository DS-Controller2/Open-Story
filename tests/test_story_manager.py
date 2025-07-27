import unittest
from unittest.mock import patch, MagicMock
from game.game_state import GameState
from game.story_manager import StoryManager

class TestStoryManager(unittest.TestCase):

    def setUp(self):
        """Set up a fresh game state for each test."""
        self.game_state = GameState()
        # We patch the StoryManager so it doesn't try to connect to a real AI during tests
        with patch('google.generativeai.GenerativeModel') as mock_model:
            self.story_manager = StoryManager(self.game_state)
            self.story_manager.model = MagicMock()

    def test_parse_ai_response_health(self):
        """Test that [HEALTH: -15] is correctly parsed."""
        ai_response = "The goblin swings its club and hits you! [HEALTH: -15]"
        cleaned_text, commands = self.story_manager._parse_ai_response(ai_response)
        self.assertEqual(cleaned_text, "The goblin swings its club and hits you!")
        self.assertEqual(commands['HEALTH'], "-15")

    def test_parse_ai_response_item(self):
        """Test that [ITEM: +key] is correctly parsed."""
        ai_response = "You find a small, rusty key on the floor. [ITEM: +rusty_key]"
        cleaned_text, commands = self.story_manager._parse_ai_response(ai_response)
        self.assertEqual(cleaned_text, "You find a small, rusty key on the floor.")
        self.assertEqual(commands['ITEM'], "+rusty_key")

    def test_parse_ai_response_location(self):
        """Test that [LOCATION: village_square] is correctly parsed."""
        ai_response = "You stumble out the door into the light. [LOCATION: village_square]"
        cleaned_text, commands = self.story_manager._parse_ai_response(ai_response)
        self.assertEqual(cleaned_text, "You stumble out the door into the light.")
        self.assertEqual(commands['LOCATION'], "village_square")