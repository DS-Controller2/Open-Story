from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class StoryCard:
    """A conditional memory that is activated by specific trigger words."""
    name: str
    entry: str
    triggers: List[str] = field(default_factory=list)
    
class MemoryManager:
    """
    Manages the AI's long-term memory, including a memory bank and story cards,
    inspired by the systems used in AI Dungeon.
    """
    def __init__(self):
        self.memory_bank: List[str] = []
        self.story_cards: Dict[str, StoryCard] = {}

    def add_to_memory_bank(self, fact: str):
        """Adds a fact to the long-term memory bank."""
        if fact not in self.memory_bank:
            self.memory_bank.append(fact)

    def create_story_card(self, name: str, entry: str, triggers: List[str]):
        """Creates and stores a new StoryCard."""
        card = StoryCard(name=name, entry=entry, triggers=[t.lower() for t in triggers])
        self.story_cards[name.lower()] = card
        return card

    def get_active_cards(self, text: str) -> List[StoryCard]:
        """
        Finds and returns all story cards whose triggers appear in the given text.
        """
        active_cards = []
        text_lower = text.lower()
        for card in self.story_cards.values():
            if any(trigger in text_lower for trigger in card.triggers):
                active_cards.append(card)
        return active_cards
