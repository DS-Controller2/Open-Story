class Player:
    def __init__(self):
        self.name = "Hero"
        self.inventory = []
        self.max_inventory_weight = 20  # Add max_inventory_weight attribute
        self.goal = ""

        # --- MODIFIED: The six core attributes ---
        self.attributes = {
            "STR": 10, # Strength: Physical power, melee damage, breaking things.
            "DEX": 10, # Dexterity: Agility, stealth, ranged attacks, lockpicking.
            "CON": 10, # Constitution: Health, stamina, resisting poison/disease.
            "INT": 10, # Intelligence: Knowledge, investigation, magic theory, puzzles.
            "WIS": 10, # Wisdom: Perception, insight, survival, willpower.
            "CHA": 10, # Charisma: Persuasion, deception, intimidation, leadership.
        }
        
        # --- MODIFIED: Health is now derived from Constitution ---
        self.base_health = 80
        self.health = self.calculate_max_health()

    def to_dict(self):
        return {
            "name": self.name,
            "inventory": self.inventory,
            "attributes": self.attributes,
            "base_health": self.base_health,
            "health": self.health,
            "max_inventory_weight": self.max_inventory_weight,
            "goal": self.goal,
        }

    @classmethod
    def from_dict(cls, data):
        player = cls()
        player.name = data["name"]
        player.inventory = data["inventory"]
        player.attributes = data["attributes"]
        player.base_health = data["base_health"]
        player.health = data["health"]
        player.max_inventory_weight = data.get("max_inventory_weight", 20)
        player.goal = data.get("goal", "")
        return player

    def get_inventory_weight(self):
        """Calculates the total weight of all items in the inventory."""
        # The inventory can contain strings or dicts. We only care about dicts with a 'weight' key.
        return sum(item.get("weight", 0) for item in self.inventory if isinstance(item, dict))


    def get_attribute_modifier(self, attr: str) -> int:
        """Calculates the D&D-style modifier for an attribute."""
        score = self.attributes.get(attr.upper())
        if score:
            return (score - 10) // 2
        return 0

    def calculate_max_health(self) -> int:
        """Calculates total health based on base + CON modifier."""
        # Each point of CON modifier adds 10 HP.
        return self.base_health + (self.get_attribute_modifier("CON") * 10)

    def display_status(self):
        """Returns a formatted string of the player's current status."""
        max_health = self.calculate_max_health()
        
        attrs_line1 = f"| STR: {self.attributes['STR']} | DEX: {self.attributes['DEX']} | CON: {self.attributes['CON']} |"
        attrs_line2 = f"| INT: {self.attributes['INT']} | WIS: {self.attributes['WIS']} | CHA: {self.attributes['CHA']} |"
        status_string = f"| Name: {self.name} | Health: {self.health}/{max_health} |"
        
        inventory_lines = []
        if self.inventory:
            inventory_lines.append(f"| Inventory ({self.get_inventory_weight()}/{self.max_inventory_weight} kg):      |")
            for item in self.inventory:
                if isinstance(item, dict):
                    inventory_lines.append(f"|   - {item.get('name', 'Unknown Item'):<18}|")
                else:
                    inventory_lines.append(f"|   - {str(item):<18}|")
        else:
            inventory_lines.append("| Inventory: Empty      |")

        all_lines = [status_string, attrs_line1, attrs_line2] + inventory_lines
        border_len = max(len(line) for line in all_lines)
        
        # Normalize line lengths
        all_lines = [line.ljust(border_len - 1) + "|" for line in all_lines]

        border = "-" * border_len
        
        return f"{border}\n" + "\n".join(all_lines) + f"\n{border}"