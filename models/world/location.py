from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from models.world.tile import TileType

class LocationType(Enum):
    ROUTE = "Route"
    CITY = "Stadt"
    BUILDING = "Gebäude"
    FOREST = "Wald"
    WATERBODIES = "Gewässer"
    CAVE = "Höhle"

DEFAULT_TILES = {
    LocationType.ROUTE: TileType.GROUND,
    LocationType.CITY: TileType.GROUND,
    LocationType.BUILDING: TileType.FLOOR,
    LocationType.FOREST: TileType.GROUND,
    LocationType.WATERBODIES: TileType.WATER,
    LocationType.CAVE: TileType.STONE
}

DEFAULT_BOUNDARIES = {
    LocationType.ROUTE: TileType.FENCE,
    LocationType.CITY: TileType.TREE,
    LocationType.BUILDING: TileType.WALL,
    LocationType.FOREST: TileType.TREE,
    LocationType.WATERBODIES: None,
    LocationType.CAVE: TileType.ROCK
}

@dataclass
class Location:
    """ Beschreibt einen Ort (Location / zusammenhängende Area) in der Spielwelt
        Besteht aus einem Raster von Tiles
    """
    id: str # unique Identifier, z.B. "city_alabastia", "lab_eich", "route_1", ...
    name: str # angezeigter Name, z.B. "Alabastia", "Labor von Prof. Eich", "Route 1"
    description: str # Beschreibt die Location für look-Befehl
    type: LocationType
    size: tuple[int, int] # width, height - innerer Bereich ohne Border
    auto_boundary: bool = True # automatische Begrenzung je nach LocationType
    special_tiles: List[dict] = field(default_factory=list) # 2D-Grid mit Tiles - nur Abweichungen vom default definieren
    npcs: List[str] = field(default_factory=list) # Liste mit IDs der NPCs
    items: List[dict] = field(default_factory=list) # {"item_id": str, "quantity": int}
    connections: Dict[str, str] = field(default_factory=dict) # z.B. {"north": "route_1"}
    npc_positions: dict[str, tuple[int, int]] = field(default_factory=dict)
    item_positions: dict[str, tuple[int, int]] = field(default_factory=dict)