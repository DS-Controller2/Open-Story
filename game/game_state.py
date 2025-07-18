from .player import Player
from .memory import MemoryManager
from .world_db import get_default_world, Location

from .player import Player
from .memory import MemoryManager
from .world_db import get_default_world, Location, World

class GameState:
    def __init__(self, api_tier: str = "free"):
        self.player = Player()
        self.memory_manager = MemoryManager()
        self.world = get_default_world()
        self.story_history = []
        self.current_location_key = "tavern"
        self.safety_level = "high"
        self.api_tier = api_tier
        self.api_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self._state_history = []
        self._current_state_index = -1
        self._max_history_size = 10

    def to_dict(self):
        return {
            "player": self.player.to_dict(),
            "memory_manager": self.memory_manager.to_dict(),
            "world": self.world.to_dict(),
            "story_history": self.story_history,
            "current_location_key": self.current_location_key,
            "safety_level": self.safety_level,
            "api_tier": self.api_tier,
            "api_calls": self.api_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }

    @classmethod
    def from_dict(cls, data):
        game_state = cls(api_tier=data.get("api_tier", "free"))
        game_state.player = Player.from_dict(data["player"])
        game_state.memory_manager = MemoryManager.from_dict(data["memory_manager"])
        game_state.world = World.from_dict(data["world"])
        game_state.story_history = data["story_history"]
        game_state.current_location_key = data["current_location_key"]
        game_state.safety_level = data["safety_level"]
        game_state.api_calls = data.get("api_calls", 0)
        game_state.total_input_tokens = data.get("total_input_tokens", 0)
        game_state.total_output_tokens = data.get("total_output_tokens", 0)
        return game_state

    def _save_snapshot(self):
        if self._current_state_index < len(self._state_history) - 1:
            self._state_history = self._state_history[:self._current_state_index + 1]
        
        # --- MODIFIED: Use to_dict for faster snapshots ---
        snapshot = self.to_dict() 
        
        self._state_history.append(snapshot)
        self._current_state_index = len(self._state_history) - 1
        if len(self._state_history) > self._max_history_size:
            self._state_history.pop(0)
            self._current_state_index -= 1

    def _load_snapshot(self, index):
        if 0 <= index < len(self._state_history):
            snapshot_dict = self._state_history[index]
            
            # --- MODIFIED: Reconstruct state from dict ---
            new_state = GameState.from_dict(snapshot_dict)
            self.player = new_state.player
            self.memory_manager = new_state.memory_manager
            self.world = new_state.world
            self.story_history = new_state.story_history
            self.current_location_key = new_state.current_location_key
            self.safety_level = new_state.safety_level
            self.api_tier = new_state.api_tier
            self.api_calls = new_state.api_calls
            self.total_input_tokens = new_state.total_input_tokens
            self.total_output_tokens = new_state.total_output_tokens
            
            self._current_state_index = index
            return True
        return False

    def undo(self):
        if self._current_state_index > 0:
            return self._load_snapshot(self._current_state_index - 1)
        return False

    def redo(self):
        if self._current_state_index < len(self._state_history) - 1:
            return self._load_snapshot(self._current_state_index + 1)
        return False

    def get_current_location_object(self) -> Location | None:
        return self.world.get_location(self.current_location_key)

    def get_current_location_description(self) -> str:
        location = self.get_current_location_object()
        return location.description if location else "an unknown place."

    def get_current_location_exits(self) -> dict:
        location = self.get_current_location_object()
        return location.exits if location else {}

    def add_to_story(self, text):
        self.story_history.append(text)

    def get_current_story(self):
        if not self.story_history:
            return "The story has not yet begun."
        return self.story_history[-1]

    def get_full_story(self):
        return "\n".join(self.story_history)