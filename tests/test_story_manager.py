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

    def test_parse_and_apply_health_command(self):
        """Test that [HEALTH: -15] is correctly parsed and applied."""
        self.game_state.player.health = 100
        ai_response = "The goblin swings its club and hits you! [HEALTH: -15]"
        cleaned_text = self.story_manager._parse_and_apply_updates(ai_response)
        self.assertEqual(self.game_state.player.health, 85)
        self.assertEqual(cleaned_text, "The goblin swings its club and hits you!")

    def test_parse_and_apply_item_command(self):
        """Test that [ITEM: +key] is correctly parsed and applied."""
        self.assertEqual(self.game_state.player.inventory, [])
        ai_response = "You find a small, rusty key on the floor. [ITEM: +rusty_key]"
        cleaned_text = self.story_manager._parse_and_apply_updates(ai_response)
        self.assertIn("rusty_key", self.game_state.player.inventory)
        self.assertEqual(cleaned_text, "You find a small, rusty key on the floor.")

    def test_parse_and_apply_location_command(self):
        """Test that [LOCATION: village_square] is correctly parsed and applied."""
        self.assertEqual(self.game_state.current_location_key, "tavern")
        ai_response = "You stumble out the door into the light. [LOCATION: village_square]"
        cleaned_text = self.story_manager._parse_and_apply_updates(ai_response)
        self.assertEqual(self.game_state.current_location_key, "village_square")
        self.assertEqual(cleaned_text, "You stumble out the door into the light.")