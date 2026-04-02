import json
from datetime import datetime
from pathlib import Path
from typing import Any

from game.context import GameContext
from models.characters.player import Player
from models.item import Item
from models.pokemon.pokemon import Pokemon
from models.world.tile import TileType
from models.world.world import World
from utils.data_loader import DataLoader


class SaveManager:
    """Verwaltet das Speichern und Laden von Spielständen"""

    def __init__(self, saves_dir: str = "saves"):
        self.saves_dir = Path(saves_dir)
        self.saves_dir.mkdir(exist_ok=True)

    def save_game(self, ctx: GameContext, save_name: str = "savegame") -> None:
        """Speichert den aktuellen Spielstand

        Args:
            ctx: GameContext mit Referenz auf world, player, npcs, ...
            save_name: Name der Speicherdatei (ohne .json)
        """
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "player": self._serialize_player(ctx.player),
            "world_state": self._serialize_world_state(ctx)
        }

        filepath = self.saves_dir / f"{save_name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        print(f"Spielstand gespeichert: {filepath}")

    def load_game(self, save_name: str, data_loader: DataLoader) -> tuple[Player, World, dict, dict, dict]:
        """Lädt einen Spielstand

        Args:
            save_name: Name der Speicherdatei (ohne .json)
            data_loader: DataLoader-Instanz zum Laden der statischen Daten

        Returns:
            Tuple mit (Player, World, NPCs, Items, Pokemons)
        """
        filepath = self.saves_dir / f"{save_name}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Spielstand nicht gefunden: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        # Welt und Datenbanken laden
        world, pokemons_db, items_db, npcs_db = data_loader.load_all()

        # Player deserialisieren
        player = self._deserialize_player(save_data["player"], data_loader, items_db)

        # World-State wiederherstellen
        self._apply_world_state(world, save_data["world_state"], npcs_db)

        for location in world.locations.values():
            data_loader.assign_random_positions(location)

        return player, world, npcs_db, items_db, pokemons_db

    @staticmethod
    def _serialize_player(player: Player) -> dict[str, Any]:
        """Serialisiert Player-Objekt für JSON"""
        return {
            "name": player.name,
            "current_location": player.current_location,
            "current_zone": player.current_zone,
            "previous_location": player.previous_location,
            "money": player.money,
            "team": [SaveManager._serialize_pokemon(p) for p in player.team],
            "inventory": [SaveManager._serialize_item(i) for i in player.inventory]
        }

    @staticmethod
    def _serialize_pokemon(pokemon: Pokemon) -> dict[str, Any]:
        """Serialisiert Pokemon-Objekt für JSON"""
        return {
            "id": pokemon.id,
            "name": pokemon.name,
            "level": pokemon.level,
            "current_stats": {
                "hp": pokemon.current_stats.hp,
                "attack": pokemon.current_stats.attack,
                "defense": pokemon.current_stats.defense,
                "initiative": pokemon.current_stats.initiative
            }
        }

    @staticmethod
    def _serialize_item(item: Item) -> dict[str, Any]:
        """Serialisiert Item-Objekt für JSON"""
        return {
            "id": item.id,
            "quantity": item.quantity
        }

    @staticmethod
    def _serialize_world_state(ctx: GameContext) -> dict[str, Any]:
        world_state = {"locations": {}}
        for loc_id, location in ctx.world.locations.items():
            npc_states = {}
            for npc_id in location.npcs:
                npc = ctx.npcs_db.get(npc_id)
                if npc:
                    npc_states[npc_id] = {"current_node": npc.current_node}
            world_state["locations"][loc_id] = {
                "items": location.items,
                "container_states": [
                    {"name": t["name"], "items": t.get("items", [])}
                    for t in location.special_tiles
                    if t["type"] == TileType.CONTAINER.value
                ],
                "npcs": location.npcs,
                "npc_states": npc_states,
            }
        return world_state

    @staticmethod
    def _deserialize_player(
            player_data: dict[str, Any],
            data_loader: DataLoader,
            items_db: dict[str, Item]
    ) -> Player:
        """Deserialisiert Player aus JSON"""

        # Team laden
        team = []
        pokemons_db = data_loader.load_pokemons()
        for poke_data in player_data.get("team", []):
            # Pokemon aus DB laden und mit gespeicherten Werten überschreiben
            base_data = pokemons_db[poke_data["id"]]
            pokemon = data_loader.create_pokemon_from_data(base_data, level=poke_data["level"])

            # Current stats überschreiben
            pokemon.current_stats.hp = poke_data["current_stats"]["hp"]
            pokemon.current_stats.attack = poke_data["current_stats"]["attack"]
            pokemon.current_stats.defense = poke_data["current_stats"]["defense"]
            pokemon.current_stats.initiative = poke_data["current_stats"]["initiative"]

            team.append(pokemon)

        # Inventar laden
        inventory = []
        for item_data in player_data.get("inventory", []):
            item_id = item_data["id"]
            if item_id in items_db:
                item = Item(
                    id=items_db[item_id].id,
                    name=items_db[item_id].name,
                    type=items_db[item_id].type,
                    heal_hp=items_db[item_id].heal_hp,
                    quantity=item_data["quantity"]
                )
                inventory.append(item)

        return Player(
            name=player_data["name"],
            current_location=player_data["current_location"],
            current_zone=player_data.get("current_zone"),
            previous_location=player_data.get("previous_location"),
            money=player_data.get("money", 300),
            team=team,
            inventory=inventory
        )

    @staticmethod
    def _apply_world_state(world: World, world_state: dict[str, Any], npcs_db: dict) -> None:
        """Wendet gespeicherten World-State an"""
        for loc_id, loc_state in world_state["locations"].items():
            if loc_id in world.locations:
                location = world.locations[loc_id]
                location.items = loc_state["items"]
                for container_state in loc_state.get("container_states", []):
                    container = next(
                        (t for t in location.special_tiles
                         if t["type"] == TileType.CONTAINER.value
                         and t.get("name") == container_state["name"]),
                        None
                    )
                    if container:
                        container["items"] = container_state["items"]
                location.npcs = loc_state["npcs"]
                for npc_id, npc_state in loc_state.get("npc_states", {}).items():
                    npc = npcs_db.get(npc_id)
                    if npc:
                        npc.current_node = npc_state["current_node"]

    def list_saves(self) -> list[tuple[str, str]]:
        """Listet alle verfügbaren Spielstände auf.

        Returns:
            Liste von (save_name, anzeigetext) Tupeln
        """
        saves = []
        for filepath in sorted(self.saves_dir.glob("*.json")):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                timestamp = data.get("timestamp", "unbekannt")
                player_name = data.get("player", {}).get("name", "?")
                label = f"{filepath.stem}  [{player_name}, {timestamp[:16]}]"
            except (json.JSONDecodeError, KeyError):
                label = filepath.stem
            saves.append((filepath.stem, label))
        return saves

    def delete_save(self, save_name: str) -> None:
        """Löscht einen Spielstand"""
        filepath = self.saves_dir / f"{save_name}.json"
        if filepath.exists():
            filepath.unlink()
            print(f"Spielstand gelöscht: {save_name}")
        else:
            print(f"Spielstand nicht gefunden: {save_name}")