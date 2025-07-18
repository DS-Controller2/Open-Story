from .player import Player
from .memory import MemoryManager
from .world_db import get_default_world, Location

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

    def _save_snapshot(self):
        if self._current_state_index < len(self._state_history) - 1:
            self._state_history = self._state_history[:self._current_state_index + 1]
        import copy
        snapshot = copy.deepcopy({
            'player': self.player,
            'memory_manager': self.memory_manager,
            'world': self.world,
            'story_history': list(self.story_history),
            'current_location_key': self.current_location_key,
            'safety_level': self.safety_level,
            'api_tier': self.api_tier,
            'api_calls': self.api_calls,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens
        })
        self._state_history.append(snapshot)
        self._current_state_index = len(self._state_history) - 1
        if len(self._state_history) > self._max_history_size:
            self._state_history.pop(0)
            self._current_state_index -= 1

    def _load_snapshot(self, index):
        if 0 <= index < len(self._state_history):
            snapshot = self._state_history[index]
            self.player = snapshot['player']
            self.memory_manager = snapshot.get('memory_manager', MemoryManager())
            self.world = snapshot.get('world', get_default_world())
            self.story_history = snapshot['story_history']
            self.current_location_key = snapshot['current_location_key']
            self.safety_level = snapshot['safety_level']
            self.api_tier = snapshot.get('api_tier', 'free')
            self.api_calls = snapshot.get('api_calls', 0)
            self.total_input_tokens = snapshot.get('total_input_tokens', 0)
            self.total_output_tokens = snapshot.get('total_output_tokens', 0)
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