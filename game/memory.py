from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import time
import networkx as nx
import spacy
from thefuzz import fuzz

@dataclass
class StoryCard:
    """A conditional memory that is activated by specific trigger words with weights."""
    name: str
    entry: str
    triggers: Dict[str, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    unlocks: List[str] = field(default_factory=list)
    negative_triggers: List[str] = field(default_factory=list)
    activation_threshold: float = 1.0
    relevance: float = 1.0
    last_activated: float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class StoryCardTemplate:
    """A template for creating StoryCards dynamically."""
    name_template: str
    entry_template: str
    triggers_template: Dict[str, float]

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class MemoryFact:
    """A fact in the memory bank with relevance scoring and tags."""
    fact: str
    relevance: float = 1.0
    last_accessed: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class FusedMemory:
    """A memory that has been processed by the contextual fusion system."""
    source: str
    content: Any
    priority: float
    explanation: str

class ContextualFusion:
    """Handles the fusion of memories from different sources."""
    def fuse(self, facts: List[Tuple[MemoryFact, str]], active_cards: List[Tuple[StoryCard, str]]) -> List[FusedMemory]:
        fused_memories = []

        for fact, explanation in facts:
            priority = fact.relevance
            fused_memories.append(FusedMemory(source="fact", content=fact, priority=priority, explanation=explanation))

        for card, explanation in active_cards:
            priority = card.relevance + 10 # Add a constant to prioritize cards
            fused_memories.append(FusedMemory(source="story_card", content=card, priority=priority, explanation=explanation))

        fused_memories.sort(key=lambda x: x.priority, reverse=True)
        
        final_memories = []
        seen_content = set()
        for mem in fused_memories:
            content_str = str(mem.content)
            if content_str not in seen_content:
                final_memories.append(mem)
                seen_content.add(content_str)

        return final_memories

class MemoryManager:
    """
    Manages the AI's long-term memory, including a memory bank with semantic search,
    a knowledge graph, and story cards, inspired by the systems used in AI Dungeon.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', decay_rate=0.01, fuzzy_threshold=80):
        self.model = SentenceTransformer(model_name)
        self.memory_bank: List[MemoryFact] = []
        self.index = None
        self.story_cards: Dict[str, StoryCard] = {}
        self.active_card_names: List[str] = []
        self.story_card_templates: Dict[str, StoryCardTemplate] = {}
        self.decay_rate = decay_rate
        self.graph = nx.Graph()
        self.nlp = spacy.load('en_core_web_sm')
        self.fuzzy_threshold = fuzzy_threshold
        self.fusion = ContextualFusion()

    def to_dict(self):
        return {
            "memory_bank": [fact.to_dict() for fact in self.memory_bank],
            "story_cards": {name: card.to_dict() for name, card in self.story_cards.items()},
            "active_card_names": self.active_card_names,
            "story_card_templates": {name: template.to_dict() for name, template in self.story_card_templates.items()},
            "decay_rate": self.decay_rate,
            "fuzzy_threshold": self.fuzzy_threshold,
            "graph": nx.node_link_data(self.graph, edges="edges")
        }

    @classmethod
    def from_dict(cls, data):
        manager = cls(decay_rate=data["decay_rate"], fuzzy_threshold=data["fuzzy_threshold"])
        manager.memory_bank = [MemoryFact.from_dict(f) for f in data["memory_bank"]]
        manager.story_cards = {name: StoryCard.from_dict(c) for name, c in data["story_cards"].items()}
        manager.active_card_names = data["active_card_names"]
        manager.story_card_templates = {name: StoryCardTemplate.from_dict(t) for name, t in data["story_card_templates"].items()}
        
        graph_data = data.get("graph")
        if graph_data:
            if "edges" in graph_data:
                manager.graph = nx.node_link_graph(graph_data, edges="edges")
            elif "links" in graph_data:
                manager.graph = nx.node_link_graph(graph_data, edges="links")
            else:
                manager.graph = nx.node_link_graph(graph_data)
        else:
            manager.graph = nx.Graph()

        manager._rebuild_index()
        return manager


    def _initialize_index(self, dimensions: int):
        """Initializes the FAISS index."""
        self.index = faiss.IndexFlatL2(dimensions)

    def _rebuild_index(self):
        """Rebuilds the FAISS index from the current memory bank."""
        if not self.memory_bank:
            self.index = None
            return
        
        dimensions = self.model.get_sentence_embedding_dimension()
        self._initialize_index(dimensions)
        embeddings = self.model.encode([fact.fact for fact in self.memory_bank])
        self.index.add(embeddings)

    def add_to_memory_bank(self, fact: str, tags: Optional[List[str]] = None):
        """
        Adds a fact to the long-term memory bank, creating a vector embedding for it,
        and adds it to the knowledge graph.
        """
        if fact not in [f.fact for f in self.memory_bank]:
            tags = tags or []
            new_fact = MemoryFact(fact=fact, tags=tags)
            self.memory_bank.append(new_fact)
            
            embedding = self.model.encode([fact])
            if self.index is None:
                self._initialize_index(embedding.shape[1])
            self.index.add(embedding)
            
            self.graph.add_node(fact, type='fact')
            for tag in tags:
                self.graph.add_node(tag, type='tag')
                self.graph.add_edge(fact, tag)

    def search_memory_bank(self, query: str, k: int = 5, tags: Optional[List[str]] = None) -> List[Tuple[MemoryFact, str]]:
        """
        Searches the memory bank for facts semantically similar to the query.
        Boosts the relevance of retrieved facts. Can filter by tags.
        Returns a list of tuples, each containing a MemoryFact and an explanation.
        """
        if not self.memory_bank or self.index is None:
            return []

        query_embedding = self.model.encode([query])
        
        if tags is None:
            distances, indices = self.index.search(query_embedding, k)
            results = []
            current_time = time.time()
            for i in indices[0]:
                if i != -1:
                    fact_obj = self.memory_bank[i]
                    fact_obj.relevance += 1.0
                    fact_obj.last_accessed = current_time
                    explanation = f"Retrieved because it is semantically similar to '{query}' with a relevance of {fact_obj.relevance:.2f}."
                    results.append((fact_obj, explanation))
            return results

        search_k = min(self.index.ntotal, k * 10)
        distances, indices = self.index.search(query_embedding, search_k)
        
        results = []
        current_time = time.time()
        tag_set = set(t.lower() for t in tags)

        for i in indices[0]:
            if i != -1:
                fact_obj = self.memory_bank[i]
                fact_tags = set(t.lower() for t in fact_obj.tags)
                if tag_set.issubset(fact_tags):
                    fact_obj.relevance += 1.0
                    fact_obj.last_accessed = current_time
                    explanation = f"Retrieved because it is semantically similar to '{query}' with tags {tags} and a relevance of {fact_obj.relevance:.2f}."
                    results.append((fact_obj, explanation))
                    if len(results) == k:
                        break
        return results

    def reason_about_facts(self, fact1: str, fact2: str) -> Optional[List[str]]:
        """
        Finds a path between two facts in the, showing their relationship.
        """
        if self.graph.has_node(fact1) and self.graph.has_node(fact2):
            try:
                path = nx.shortest_path(self.graph, source=fact1, target=fact2)
                return path
            except nx.NetworkXNoPath:
                return None
        return None

    def decay_relevance_scores(self):
        """Decays the relevance scores of all facts in the memory bank."""
        current_time = time.time()
        for fact_obj in self.memory_bank:
            time_diff = current_time - fact_obj.last_accessed
            decay_amount = time_diff * self.decay_rate
            fact_obj.relevance = max(0, fact_obj.relevance - decay_amount)

    def decay_card_relevance_scores(self):
        """Decays the relevance scores of all story cards."""
        current_time = time.time()
        for card in self.story_cards.values():
            time_diff = current_time - card.last_activated
            decay_amount = time_diff * self.decay_rate
            card.relevance = max(0, card.relevance - decay_amount)

    def prune_memories(self, fact_threshold: float, card_threshold: float):
        """Prunes memories below a given relevance threshold."""
        self.memory_bank = [fact for fact in self.memory_bank if fact.relevance >= fact_threshold]
        self._rebuild_index()
        
        self.story_cards = {name: card for name, card in self.story_cards.items() if card.relevance >= card_threshold}

    def create_story_card(self, name: str, entry: str, triggers: Dict[str, float], dependencies: List[str] = [], unlocks: List[str] = [], negative_triggers: List[str] = []):
        """Creates and stores a new StoryCard with weighted triggers, dependencies, unlocks, and negative triggers."""
        card = StoryCard(name=name, entry=entry, triggers={t.lower(): w for t, w in triggers.items()}, dependencies=dependencies, unlocks=unlocks, negative_triggers=negative_triggers)
        self.story_cards[name.lower()] = card
        return card

    def create_story_card_template(self, name: str, name_template: str, entry_template: str, triggers_template: Dict[str, float]):
        """Creates and stores a new StoryCardTemplate."""
        template = StoryCardTemplate(name_template, entry_template, triggers_template)
        self.story_card_templates[name] = template

    def generate_card_from_template(self, template_name: str, context: Dict[str, str]) -> Optional[StoryCard]:
        """Generates a StoryCard from a template and context."""
        if template_name not in self.story_card_templates:
            return None
        
        template = self.story_card_templates[template_name]
        
        card_name = template.name_template.format(**context)
        card_entry = template.entry_template.format(**context)
        card_triggers = {k.format(**context).lower(): v for k, v in template.triggers_template.items()}
        
        return self.create_story_card(card_name, card_entry, card_triggers)

    def get_active_cards(self, text: str) -> List[Tuple[StoryCard, str]]:
        """
        Finds and returns all story cards that are active based on triggers, dependencies, and unlocks,
        using fuzzy matching for triggers and negative triggers.
        Returns a list of tuples, each containing a StoryCard and an explanation.
        """
        text_lower = text.lower()
        newly_activated_cards = []
        current_time = time.time()

        for card in self.story_cards.values():
            if card.name.lower() in self.active_card_names:
                continue

            dependencies_met = all(dep.lower() in self.active_card_names for dep in card.dependencies)
            if not dependencies_met:
                continue

            negative_trigger_found = False
            for neg_trigger in card.negative_triggers:
                if fuzz.partial_ratio(neg_trigger, text_lower) >= self.fuzzy_threshold:
                    negative_trigger_found = True
                    break
            if negative_trigger_found:
                continue

            activation_score = 0.0
            activated_triggers = []
            for trigger, weight in card.triggers.items():
                if fuzz.partial_ratio(trigger, text_lower) >= self.fuzzy_threshold:
                    activation_score += weight
                    activated_triggers.append(trigger)
            
            if activation_score >= card.activation_threshold:
                card.relevance += 1.0
                card.last_activated = current_time
                explanation = f"Activated because the following triggers were found: {', '.join(activated_triggers)}. Activation score: {activation_score:.2f}."
                newly_activated_cards.append((card, explanation))
                self.active_card_names.append(card.name.lower())

                for unlocked_card_name in card.unlocks:
                    unlocked_card = self.story_cards.get(unlocked_card_name.lower())
                    if unlocked_card:
                        unlocked_card.activation_threshold *= 0.8
        
        return newly_activated_cards

    def retrieve_memories(self, query: str, k: int = 5, tags: Optional[List[str]] = None) -> List[FusedMemory]:
        """
        Retrieves and fuses relevant memories from both the Memory Bank and Story Cards.
        """
        facts = self.search_memory_bank(query, k, tags)
        active_cards = self.get_active_cards(query)
        
        return self.fusion.fuse(facts, active_cards)
