import unittest
from game.game_state import GameState

class TestGameState(unittest.TestCase):

    def test_initialization(self):
        """Test that the game state starts correctly."""
        gs = GameState()
        self.assertEqual(gs.current_location_key, "tavern")
        self.assertEqual(gs.get_current_location_description(), "a dimly lit tavern, smelling of stale ale and sawdust. A single door leads out to the village square, and a grimy curtain covers an exit to the back.")
        self.assertEqual(gs.story_history, [])

    def test_story_history(self):
        """Test adding to and retrieving from story history."""
        gs = GameState()
        self.assertEqual(gs.get_current_story(), "The story has not yet begun.")
        gs.add_to_story("First line.")
        self.assertEqual(gs.get_current_story(), "First line.")
        gs.add_to_story("Second line.")
        self.assertEqual(gs.get_current_story(), "Second line.")
        self.assertEqual(gs.get_full_story(), "First line.\nSecond line.")
