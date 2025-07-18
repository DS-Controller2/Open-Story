from dataclasses import dataclass, field
from typing import List, Dict

# --- World Building Blocks ---

@dataclass
class WorldInfoEntry:
    """A piece of lore or information about the world."""
    name: str
    entry: str
    # Triggers can be used to make this info appear in context, similar to Story Cards
    triggers: List[str] = field(default_factory=list)

@dataclass
class Race:
    name: str
    description: str
    
@dataclass
class Faction:
    name: str
    description: str

@dataclass
class Class:
    name: str
    description: str
    # Base attributes for this class
    attributes: Dict[str, int] = field(default_factory=dict)

@dataclass
class Location:
    key: str # Unique identifier, e.g., "tavern"
    name: str
    description: str
    exits: Dict[str, str] = field(default_factory=dict)

# --- The World Itself ---

@dataclass
class World:
    name: str
    genre: str
    description: str
    races: Dict[str, Race] = field(default_factory=dict)
    factions: Dict[str, Faction] = field(default_factory=dict)
    classes: Dict[str, Class] = field(default_factory=dict)
    locations: Dict[str, Location] = field(default_factory=dict)
    world_info: List[WorldInfoEntry] = field(default_factory=list)

    def get_location(self, key: str) -> Location | None:
        return self.locations.get(key)

# --- Default World Definition ---

def get_default_world() -> World:
    """
    Returns a pre-defined High Fantasy world to serve as the default.
    """
    
    # Locations
    tavern = Location(
        key="tavern",
        name="The Weary Wanderer Tavern",
        description="A dimly lit tavern, smelling of stale ale and sawdust. A few patrons are scattered around, and a fire crackles in the hearth.",
        exits={"out": "village_square"}
    )
    village_square = Location(
        key="village_square",
        name="Village Square",
        description="A bustling village square with a central well. Merchants hawk their wares from colorful stalls.",
        exits={"in": "tavern"}
    )

    # Classes
    warrior = Class(
        name="Warrior",
        description="A master of arms and armor, strong and resilient.",
        attributes={"STR": 3, "DEX": 1, "CON": 2} # Points to add to base
    )
    mage = Class(
        name="Mage",
        description="A scholar of the arcane, wielding powerful magic.",
        attributes={"INT": 3, "WIS": 2, "CON": -1}
    )
    rogue = Class(
        name="Rogue",
        description="A cunning and agile operative, skilled in stealth and subterfuge.",
        attributes={"DEX": 3, "CHA": 2, "STR": -1}
    )

    # World
    default_world = World(
        name="Aethelgard",
        genre="High Fantasy",
        description="A classic fantasy world of magic, monsters, and adventure.",
        locations={
            "tavern": tavern,
            "village_square": village_square
        },
        classes={
            "warrior": warrior,
            "mage": mage,
            "rogue": rogue
        }
    )
    
    return default_world

def create_custom_world() -> World:
    """
    Guides the user through creating a custom world.
    """
    print("\n--- World Creation ---")
    name = input("Enter the name of your world: ")
    genre = input("Enter the genre of your world (e.g., Sci-Fi, Fantasy, Cyberpunk): ")
    description = input("Enter a brief description of your world: ")

    world = World(name=name, genre=genre, description=description)

    print("\n--- Starting Location ---")
    print("Let's create the first location where your story will begin.")
    loc_key = input("Enter a unique key for the location (e.g., 'home_base'): ")
    loc_name = input(f"Enter the name of the location (e.g., 'The Rusty Cog Cantina'): ")
    loc_desc = input(f"Enter a description for {loc_name}: ")
    world.locations[loc_key] = Location(key=loc_key, name=loc_name, description=loc_desc)

    print("\n--- Character Classes ---")
    print("Define at least one character class.")
    while True:
        class_name = input("Enter a class name (or 'done' to finish): ")
        if class_name.lower() == 'done':
            if world.classes:
                break
            else:
                print("You must define at least one class.")
                continue
        class_desc = input(f"Enter a description for the {class_name}: ")
        attributes = {}
        print("Set the attribute modifiers for this class (e.g., STR 2, DEX -1).")
        while True:
            attr_str = input("Enter attribute modifier (or 'done'): ").upper()
            if attr_str.lower() == 'done':
                break
            try:
                stat, value = attr_str.split()
                attributes[stat] = int(value)
            except ValueError:
                print("Invalid format. Please use 'STAT #', e.g., 'STR 2'.")
        world.classes[class_name.lower()] = Class(name=class_name, description=class_desc, attributes=attributes)

    return world