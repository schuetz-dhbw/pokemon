from dataclasses import dataclass

from models.characters.npc import NPC
from models.characters.player import Player
from models.item import Item
from models.world.world import World


@dataclass
class GameContext:
    """Zentraler Spielzustand – wird durch alle Spiellogik-Funktionen gereicht"""
    player: Player
    world: World
    npcs_db: dict[str, NPC]
    items_db: dict[str, Item]
    pokemons_db: dict[int, dict]