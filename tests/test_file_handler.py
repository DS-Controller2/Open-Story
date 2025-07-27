import unittest
import os
import pickle
from game.game_state import GameState
import utils.file_handler as file_handler

class TestFileHandler(unittest.TestCase):
    
    def setUp(self):
        """Create a dummy save directory and filename for testing."""
        self.test_save_dir = "test_saves"
        file_handler.SAVE_DIRECTORY = self.test_save_dir
        self.test_filename = "test_save_1"
        if not os.path.exists(self.test_save_dir):
            os.makedirs(self.test_save_dir)

    def tearDown(self):
        """Clean up dummy files and directories after tests."""
        test_filepath = os.path.join(self.test_save_dir, f"{self.test_filename}.json")
        if os.path.exists(test_filepath):
            os.remove(test_filepath)
        if os.path.exists(self.test_save_dir):
            # Check if the directory is empty before trying to remove it
            if not os.listdir(self.test_save_dir):
                os.rmdir(self.test_save_dir)

    def test_save_and_load_game(self):
        """Test that a game state can be saved and reloaded accurately."""
        gs_to_save = GameState()
        gs_to_save.player.name = "Tester"
        gs_to_save.player.inventory.append("test_item")
        gs_to_save.add_to_story("A test event happened.")

        # Save the game
        result = file_handler.save_game(gs_to_save, self.test_filename)
        self.assertTrue(result)
        
        # Load the game
        gs_loaded = file_handler.load_game(self.test_filename)
        self.assertIsNotNone(gs_loaded)
        self.assertEqual(gs_loaded.player.name, "Tester")
        self.assertIn("test_item", gs_loaded.player.inventory)
        self.assertEqual(gs_loaded.get_current_story(), "A test event happened.")