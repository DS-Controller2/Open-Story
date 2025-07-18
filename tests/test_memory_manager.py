import unittest
import time
from game.memory import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Set up a new MemoryManager instance for each test."""
        self.memory_manager = MemoryManager(fuzzy_threshold=80)

    def test_add_and_search_memory_bank(self):
        """Test adding a fact and searching for it."""
        self.memory_manager.add_to_memory_bank("The sky is blue.", tags=["nature"])
        results = self.memory_manager.search_memory_bank("What color is the sky?")
        self.assertIn("The sky is blue.", [fact[0].fact for fact in results])

    def test_relevance_scoring(self):
        """Test that relevance scores are boosted and decay over time."""
        self.memory_manager.add_to_memory_bank("The cat is on the mat.")
        
        # Access the fact to boost its relevance
        self.memory_manager.search_memory_bank("Where is the cat?")
        fact = self.memory_manager.memory_bank[0]
        self.assertGreater(fact.relevance, 1.0)

        # Test decay
        fact.last_accessed = time.time() - 10
        self.memory_manager.decay_relevance_scores()
        self.assertLess(fact.relevance, 2.0)

    def test_fact_tagging(self):
        """Test adding and searching for facts with tags."""
        self.memory_manager.add_to_memory_bank("The king is named Arthur.", tags=["king", "arthur"])
        self.memory_manager.add_to_memory_bank("The queen is named Guinevere.", tags=["queen", "guinevere"])
        
        results = self.memory_manager.search_memory_bank("Who is the king?", tags=["king"])
        self.assertIn("The king is named Arthur.", [fact[0].fact for fact in results])
        self.assertEqual(len(results), 1)

    def test_knowledge_graph(self):
        """Test the knowledge graph integration."""
        self.memory_manager.add_to_memory_bank("The sword is in the stone.", tags=["sword", "stone"])
        self.memory_manager.add_to_memory_bank("The stone is in the forest.", tags=["stone", "forest"])
        
        path = self.memory_manager.reason_about_facts("The sword is in the stone.", "The stone is in the forest.")
        self.assertIsNotNone(path)
        self.assertEqual(path, ["The sword is in the stone.", "stone", "The stone is in the forest."])

    def test_story_card_weighted_triggers(self):
        """Test that story cards are activated based on weighted triggers."""
        self.memory_manager.create_story_card(
            name="Cursed Locket",
            entry="A locket that drains life force.",
            triggers={"locket": 1.0, "cursed": 0.5}
        )
        
        # Should not activate
        cards = self.memory_manager.get_active_cards("I found a cursed item.")
        self.assertEqual(len(cards), 0)

        # Should activate
        cards = self.memory_manager.get_active_cards("I found a cursed locket.")
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0][0].name, "Cursed Locket")

    def test_dynamic_card_generation(self):
        """Test generating a story card from a template."""
        self.memory_manager.create_story_card_template(
            name="item_pickup",
            name_template="Picked up {item_name}",
            entry_template="You have picked up the {item_name}. It is {description}.",
            triggers_template={"{item_name}": 1.0}
        )
        
        context = {"item_name": "Golden Key", "description": "ornate and heavy"}
        card = self.memory_manager.generate_card_from_template("item_pickup", context)
        
        self.assertIsNotNone(card)
        self.assertEqual(card.name, "Picked up Golden Key")
        self.assertIn("golden key", card.triggers)

    def test_card_dependencies(self):
        """Test that card dependencies and unlocks work correctly."""
        self.memory_manager.create_story_card(
            name="Find Key",
            entry="You found a key.",
            triggers={"key": 1.0},
            unlocks=["Unlock Chest"]
        )
        self.memory_manager.create_story_card(
            name="Unlock Chest",
            entry="You unlocked the chest.",
            triggers={"chest": 1.0},
            dependencies=["Find Key"]
        )

        # Try to unlock the chest first (should fail)
        cards = self.memory_manager.get_active_cards("I will unlock the chest.")
        self.assertEqual(len(cards), 0)

        # Find the key first
        self.memory_manager.get_active_cards("I found the key.")
        
        # Now try to unlock the chest (should succeed)
        cards = self.memory_manager.get_active_cards("I will unlock the chest.")
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0][0].name, "Unlock Chest")

    def test_fuzzy_and_negative_triggers(self):
        """Test fuzzy and negative triggers."""
        self.memory_manager.create_story_card(
            name="Haunted Mansion",
            entry="A spooky old mansion.",
            triggers={"mansion": 1.0},
            negative_triggers=["not haunted", "realtor"]
        )

        # Test fuzzy trigger
        cards = self.memory_manager.get_active_cards("I see a mansoin on the hill.")
        self.assertEqual(len(cards), 1)

        # Test negative trigger
        cards = self.memory_manager.get_active_cards("The realtor said the mansion is not haunted.")
        self.assertEqual(len(cards), 0)

    def test_unified_retrieval_and_fusion(self):
        """Test the unified memory retrieval and contextual fusion."""
        self.memory_manager.add_to_memory_bank("The village is called Oakhaven.", tags=["location"])
        self.memory_manager.create_story_card(
            name="Oakhaven Rumor",
            entry="The villagers whisper of a treasure in the woods.",
            triggers={"oakhaven": 1.0}
        )

        memories = self.memory_manager.retrieve_memories("What's the deal with Oakhaven?")
        
        self.assertEqual(len(memories), 2)
        self.assertEqual(memories[0].source, "story_card")
        self.assertEqual(memories[1].source, "fact")
        self.assertIn("Activated because", memories[0].explanation)

    def test_memory_pruning(self):
        """Test that memory pruning removes irrelevant facts and cards."""
        self.memory_manager.add_to_memory_bank("Fact 1")
        self.memory_manager.add_to_memory_bank("Fact 2")
        self.memory_manager.create_story_card("Card 1", "Entry 1", {"trigger1": 1.0})
        
        # Lower relevance
        self.memory_manager.memory_bank[0].relevance = 0.1
        self.memory_manager.story_cards["card 1"].relevance = 0.1

        self.memory_manager.prune_memories(fact_threshold=0.5, card_threshold=0.5)

        self.assertEqual(len(self.memory_manager.memory_bank), 1)
        self.assertEqual(self.memory_manager.memory_bank[0].fact, "Fact 2")
        self.assertEqual(len(self.memory_manager.story_cards), 0)

if __name__ == '__main__':
    unittest.main()