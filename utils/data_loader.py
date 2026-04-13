import json
import random
from pathlib import Path
from typing import Any

from models.characters.npc import NPC, NPCType
from models.item import Item, ItemType
from models.pokemon.attack import Attack, AttackCategory, StatusEffect, StatusEffectType
from models.pokemon.pokemon import Pokemon, Evolution
from models.pokemon.pokemon_type import PokemonType
from models.pokemon.stats import Stats
from models.world.location import Location, LocationType
from models.world.tile import HabitatType
from models.world.world import World

ATTACK_CATEGORY_MAP: dict[str, AttackCategory] = {
    "physical": AttackCategory.PHYSICAL,
    "status": AttackCategory.STATUS,
    "special": AttackCategory.SPECIAL
}

STATUS_EFFECT_TYPE_MAP: dict[str, StatusEffectType] = {
    "poison": StatusEffectType.POISON,
    "burn": StatusEffectType.BURN,
    "stat_change": StatusEffectType.STAT_CHANGE
}

class DataLoader:
    """Lädt statische Spieldaten aus JSON-Dateien"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def load_json(self, filename: str) -> list[dict[str, Any]] | dict[str, Any]:
        """Lädt eine JSON-Datei"""
        filepath = self.data_dir / filename
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_items(self) -> dict[str, Item]:
        """Lädt alle Items aus items.json"""
        items_data = self.load_json("items.json")
        items = {}

        for item_data in items_data:
            if not item_data.get("id") or not item_data.get("name"):
                raise ValueError(f"Item ohne 'id' oder 'name' gefunden: {item_data}")
            if not item_data.get("type"):
                raise ValueError(f"Item '{item_data.get('id')}' hat keinen Typ.")
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                type=ItemType(item_data["type"]),
                heal_hp=item_data.get("heal_hp"),
                quantity=1
            )
            items[item.id] = item

        return items

    def load_pokemons(self) -> dict[int, dict[str, Any]]:
        """Lädt Pokemon-Datenbank aus pokemons.json

        Returns:
            Dict mit Pokemon-ID als Key und Pokemon-Rohdaten als Value
            (Wird erst bei Bedarf zu Pokemon-Instanzen konvertiert)
        """
        pokemons_data = self.load_json("pokemons.json")
        pokemons_db = {}

        for poke_data in pokemons_data:
            pokemons_db[poke_data["id"]] = poke_data

        return pokemons_db

    @staticmethod
    def create_pokemon_from_data(poke_data: dict[str, Any], level: int = 5) -> Pokemon:
        """Erstellt eine Pokemon-Instanz aus Rohdaten

        Args:
            poke_data: Pokemon-Rohdaten aus JSON
            level: Level des Pokemon (default: 5)
        """

        if not poke_data.get("attacks"):
            raise ValueError(f"Pokémon '{poke_data.get('id')}' hat keine Attacken definiert.")
        if not 0 <= poke_data.get("spawn_probability", 0) <= 1:
            raise ValueError(f"Pokémon '{poke_data.get('id')}': spawn_probability muss zwischen 0 und 1 liegen.")

        # Types parsen
        types = [PokemonType(t) for t in poke_data["types"]]

        # Stats parsen
        stats_data = poke_data["stats"]
        base_stats = Stats(
            hp=stats_data["hp"],
            attack=stats_data["attack"],
            defense=stats_data["defense"],
            initiative=stats_data["initiative"]
        )

        # Current stats = base stats (später mit Level-Berechnung)
        current_stats = Stats(
            hp=stats_data["hp"],
            attack=stats_data["attack"],
            defense=stats_data["defense"],
            initiative=stats_data["initiative"]
        )

        # Attacks parsen
        attacks = []
        for attack_data in poke_data["attacks"]:
            # Status Effect parsen (optional)
            status_effect = None
            if attack_data.get("status_effect"):
                se_data = attack_data["status_effect"]
                status_effect = StatusEffect(
                    effect_type=STATUS_EFFECT_TYPE_MAP[se_data["effect_type"]],
                    chance=se_data["chance"],
                    target_stat=se_data.get("target_stat"),
                    change=se_data.get("change"),
                    duration=se_data.get("duration")
                )

            attack = Attack(
                name=attack_data["name"],
                type=PokemonType(attack_data["type"]),
                power=attack_data["power"],
                accuracy=attack_data["accuracy"],
                category=ATTACK_CATEGORY_MAP[attack_data["category"]],
                required_level=attack_data["required_level"],
                status_effect=status_effect
            )
            attacks.append(attack)

        # Habitats parsen
        habitats = [HabitatType(h) for h in poke_data.get("habitat", [])]

        # Evolution parsen
        evolution_data = poke_data.get("evolution")
        evolution = Evolution(
            evolves_to=evolution_data["evolves_to"],
            evolution_level=evolution_data["evolution_level"]
        ) if evolution_data else None

        return Pokemon(
            id=poke_data["id"],
            name=poke_data["name"],
            types=types,
            base_stats=base_stats,
            current_stats=current_stats,
            level=level,
            attacks=attacks,
            habitats=habitats,
            catch_rate=poke_data["catch_rate"],
            spawn_probability=poke_data["spawn_probability"],
            evolution=evolution
        )

    @staticmethod
    def assign_random_positions(location: Location) -> None:
        """Weist NPCs und Items zufällige Positionen im inneren Bereich zu"""
        width, height = location.size
        occupied = {(t["x"], t["y"]) for t in location.special_tiles}
        free = [(x, y) for x in range(width) for y in range(height) if (x, y) not in occupied]
        random.shuffle(free)

        for npc_id in location.npcs:
            if free:
                location.npc_positions[npc_id] = free.pop()

        for item in location.items:
            if free:
                location.item_positions[item["item_id"]] = free.pop()

    def load_npcs(self, items_db: dict[str, Item]) -> dict[str, NPC]:
        """Lädt alle NPCs aus npcs.json"""
        npcs_data = self.load_json("npcs.json")
        npcs = {}

        for npc_data in npcs_data:
            if not npc_data.get("id") or not npc_data.get("name"):
                raise ValueError(f"NPC ohne 'id' oder 'name' gefunden: {npc_data}")
            for item_entry in npc_data.get("inventory", []):
                if item_entry["item_id"] not in items_db:
                    raise ValueError(f"NPC '{npc_data.get('id')}': Item '{item_entry['item_id']}' nicht in items_db.")
            # Inventar aus items_db laden
            inventory = []
            for item_entry in npc_data.get("inventory", []):
                item_id = item_entry["item_id"]
                quantity = item_entry["quantity"]
                if item_id in items_db:
                    item = Item(
                        id=items_db[item_id].id,
                        name=items_db[item_id].name,
                        type=items_db[item_id].type,
                        heal_hp=items_db[item_id].heal_hp,
                        quantity=quantity
                    )
                    inventory.append(item)

            npc = NPC(
                name=npc_data["name"],
                npc_type=NPCType(npc_data["npc_type"]),
                description=npc_data.get("description", ""),
                dialogue=npc_data.get("dialogue", []),
                team=[],  # Team wird später bei Bedarf geladen
                inventory=inventory
            )
            npcs[npc_data["id"]] = npc

        return npcs

    def load_locations(self) -> dict[str, Location]:
        """Lädt alle Locations aus locations.json"""
        locations_data = self.load_json("locations.json")
        locations = {}

        for loc_data in locations_data:
            if not loc_data.get("id") or not loc_data.get("name"):
                raise ValueError(f"Location ohne 'id' oder 'name' gefunden: {loc_data}")
            size = loc_data.get("size")
            if not size or len(size) != 2 or any(s <= 0 for s in size):
                raise ValueError(f"Location '{loc_data.get('id')}': ungültige 'size' {size}.")
            # Special tiles parsen
            special_tiles = []
            for tile_data in loc_data.get("special_tiles", []):
                tile_dict = {
                    "x": tile_data["x"],
                    "y": tile_data["y"],
                    "type": tile_data["type"]
                }

                # Optionale Felder
                if "name" in tile_data:
                    tile_dict["name"] = tile_data["name"]
                if "description" in tile_data:
                    tile_dict["description"] = tile_data["description"]
                if "items" in tile_data:
                    tile_dict["items"] = tile_data["items"]

                special_tiles.append(tile_dict)

            # Items parsen
            items = loc_data.get("items", [])
            width, height = loc_data["size"]

            location = Location(
                id=loc_data["id"],
                name=loc_data["name"],
                description=loc_data["description"],
                type=LocationType(loc_data["type"]),
                size = (int(width), int(height)),
                auto_boundary=loc_data.get("auto_boundary", True),
                special_tiles=special_tiles,
                npcs=loc_data.get("npcs", []),
                items=items,
                connections=loc_data.get("connections", {})
            )
            locations[location.id] = location
            self.assign_random_positions(location)

        return locations

    def load_world(self) -> World:
        """Lädt die komplette Spielwelt"""
        locations = self.load_locations()

        world = World(
            locations=locations,
            starting_location="city_alabastia"
        )

        return world

    def load_all(self) -> tuple[World, dict[int, dict], dict[str, Item], dict[str, NPC]]:
        """Lädt alle statischen Spieldaten

        Returns:
            Tuple mit (World, Pokemon-DB, Items-DB, NPCs-DB)
        """
        world = self.load_world()
        pokemons_db = self.load_pokemons()
        items_db = self.load_items()
        npcs_db = self.load_npcs(items_db)

        # Kreuzreferenzen prüfen
        for loc_id, location in world.locations.items():
            for npc_id in location.npcs:
                if npc_id not in npcs_db:
                    raise ValueError(f"Location '{loc_id}': NPC '{npc_id}' nicht in npcs_db.")
            for item_entry in location.items:
                if item_entry["item_id"] not in items_db:
                    raise ValueError(f"Location '{loc_id}': Item '{item_entry['item_id']}' nicht in items_db.")

        return world, pokemons_db, items_db, npcs_db