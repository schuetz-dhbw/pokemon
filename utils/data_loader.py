import json
from pathlib import Path
from typing import Any

from models.characters.npc import NPC, NPCType
from models.item import Item, ItemType
from models.pokemon.attack import Attack, AttackCategory, StatusEffect, StatusEffectType
from models.pokemon.pokemon import Pokemon
from models.pokemon.pokemon_type import PokemonType
from models.pokemon.stats import Stats
from models.world.location import Location, LocationType
from models.world.tile import HabitatType
from models.world.world import World


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

    def create_pokemon_from_data(self, poke_data: dict[str, Any], level: int = 5) -> Pokemon:
        """Erstellt eine Pokemon-Instanz aus Rohdaten

        Args:
            poke_data: Pokemon-Rohdaten aus JSON
            level: Level des Pokemon (default: 5)
        """
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
                    effect_type=StatusEffectType(se_data["effect_type"]),
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
                category=AttackCategory(attack_data["category"]),
                required_level=attack_data["required_level"],
                status_effect=status_effect
            )
            attacks.append(attack)

        # Habitats parsen
        habitats = [HabitatType(h) for h in poke_data.get("habitat", [])]

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
            spawn_probability=poke_data["spawn_probability"]
        )

    def load_npcs(self, items_db: dict[str, Item]) -> dict[str, NPC]:
        """Lädt alle NPCs aus npcs.json"""
        npcs_data = self.load_json("npcs.json")
        npcs = {}

        for npc_data in npcs_data:
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
            # Special tiles parsen
            special_tiles = []
            for tile_data in loc_data.get("special_tiles", []):
                tile_dict = {
                    "x": tile_data["x"],
                    "y": tile_data["y"],
                    "type": tile_data["type"]
                }

                # Optionale Felder
                if "encounter_rate" in tile_data:
                    tile_dict["encounter_rate"] = tile_data["encounter_rate"]
                if "habitat" in tile_data:
                    tile_dict["habitat"] = tile_data["habitat"]
                if "door_target" in tile_data:
                    tile_dict["door_target"] = tile_data["door_target"]

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

        return world, pokemons_db, items_db, npcs_db