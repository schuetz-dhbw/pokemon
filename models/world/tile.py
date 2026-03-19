from dataclasses import dataclass
from enum import Enum

class TileType(Enum):
    """" Art eines Feldes in der Spielwelt """
    # Untergrund (begehbar)
    GROUND = "Erdboden"
    FLOOR = "Fußboden"
    TALL_GRASS = "Hohes Gras"
    WATER = "Wasser"
    WOOD = "Holz"
    STONE = "Stein"

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
    """ Lebensraum für wilde Pokémon-Begegnungen """
    GRASS = "Gras"
    WATER = "Wasser"
    FOREST = "Wald"
    CAVE = "Höhle"

@dataclass
class Tile:
    """ Einzelnes Feld im Spielwelt-Raster (Location-Grid) """
    type: TileType
    walkable: bool
    encounter_rate: float = 0.0 # Wahrscheinlichkeit für das Auftauchen wilder Pokemon
    habitat: HabitatType | None = None
    requires: str | None = None # z.B. Fähigkeit "surfen" oder Item "Schlüssel" oder Level 5