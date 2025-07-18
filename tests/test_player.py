import unittest
from game.player import Player

class TestPlayer(unittest.TestCase):

    def test_initialization(self):
        """Test that the player starts with default values."""
        player = Player()
        self.assertEqual(player.name, "Hero")
        self.assertEqual(player.health, 100)
        self.assertEqual(player.inventory, [])

    def test_display_status(self):
        """Test the status string formatting."""
        player = Player()
        player.name = "Test"
        player.inventory.append("torch")
        status = player.display_status()
        self.assertIn("| Name: Test |", status)
        self.assertIn("| Health: 100/100 |", status)
        self.assertIn("| Inventory: torch |", status)