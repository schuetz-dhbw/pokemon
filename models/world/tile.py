from dataclasses import dataclass
from enum import Enum

class TileType(Enum):
    """" Art eines Feldes in der Spielwelt """
    # Untergrund (begehbar, aber nicht als Zone betretbar)
    GROUND = "Erdboden"
    FLOOR = "Fußboden"
    WOOD = "Holz"
    STONE = "Stein"

    # Zonen (betretbar via walk, triggern Pokemon-Encounter)
    GRASS = "Gras"
    WATER = "Wasser"

    # Hindernisse (nicht begehbar)
    TREE = "Baum"
    ROCK = "Fels"
    WALL = "Mauer"
    FENCE = "Zaun"

    # Interaktiv
    DOOR = "Tür"
    BUILDING = "Gebäude"
    CONTAINER = "Container"

class HabitatType(Enum):
    """Lebensräume für wilde Pokémon – Teilmenge der betretbaren TileTypes.
    Erweiterbar um CAVE, FOREST etc. – TILE_TO_HABITAT entsprechend anpassen."""
    GRASS = "Gras"
    WATER = "Wasser"

# Verbindet betretbare Zonen (TileType) mit Pokémon-Lebensräumen (HabitatType).
# Nur TileTypes die hier eingetragen sind, können als Zone betreten werden.
TILE_TO_HABITAT: dict[TileType, HabitatType] = {
    TileType.GRASS: HabitatType.GRASS,
    TileType.WATER: HabitatType.WATER,
}