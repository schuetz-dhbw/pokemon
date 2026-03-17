from models.world.location import Location, DEFAULT_BOUNDARIES, DEFAULT_TILES
from models.world.tile import TileType
from models.world.world import World

# Symbole für jeden TileType
TILE_SYMBOLS: dict[TileType, str] = {
    TileType.GROUND:     "⬛",
    TileType.FLOOR:      "⬜",
    TileType.TALL_GRASS: '🟩',
    TileType.WATER:      "🟦",
    TileType.WOOD:       "🟫",
    TileType.STONE:      "🔳",
    TileType.TREE:       "🌳",
    TileType.ROCK:       "⛰️️",
    TileType.WALL:       "➖",
    TileType.FENCE:      "✖️️",
    TileType.DOOR:       "🚪",
    TileType.BUILDING:   "🏠"
}

# Himmelsrichtungen (englische Keys) mit Pfeilsymbolen für den Border
DIRECTION_SYMBOLS: dict[str, str] = {
    "north": "⬆️",
    "south": "⬇️",
    "east":  "➡️",
    "west":  "⬅️",
}

# Symbol für nicht-direktionale Verbindungen (Gebäude, Ausgänge)
CONNECTION_SYMBOL = "🔀"

def _apply_exits_to_border(
    grid: list[list[str]],
    connections: dict[str, str],
    inner_width: int,
    inner_height: int
) -> None:
    """Setzt Pfeil-Symbole in den Border für Himmelsrichtungs-Verbindungen.
    Verändert das Grid in-place.

    Args:
        grid: Das vollständige Grid inkl. Border (inner + 2 in jeder Dimension)
        connections: Verbindungen der Location
        inner_width: Breite des inneren Bereichs
        inner_height: Höhe des inneren Bereichs
    """
    mid_x = inner_width // 2 + 1   # +1 wegen Border-Offset
    mid_y = inner_height // 2 + 1  # +1 wegen Border-Offset

    for direction, symbol in DIRECTION_SYMBOLS.items():
        if direction not in connections:
            continue
        match direction:
            case "north":
                grid[0][mid_x] = symbol
            case "south":
                grid[inner_height + 1][mid_x] = symbol
            case "east":
                grid[mid_y][inner_width + 1] = symbol
            case "west":
                grid[mid_y][0] = symbol


def render_location(location: Location) -> str:
    """Rendert eine Location als ASCII-Grid.
    size beschreibt den inneren Bereich, der Border wird außen drum gelegt.

    Args:
        location: Die zu rendernde Location

    Returns:
        ASCII-Darstellung der Location als String
    """
    inner_width, inner_height = location.size

    # Grid mit Default-Tile füllen (size = innerer Bereich)
    default_tile = DEFAULT_TILES.get(location.type, TileType.GROUND)
    default_symbol = TILE_SYMBOLS[default_tile]
    grid = [[default_symbol for _ in range(inner_width)] for _ in range(inner_height)]

    # Special tiles eintragen (Koordinaten beziehen sich auf inneren Bereich)
    for tile_data in location.special_tiles:
        x, y = tile_data["x"], tile_data["y"]
        tile_type = TileType(tile_data["type"])
        if 0 <= x < inner_width and 0 <= y < inner_height:
            grid[y][x] = TILE_SYMBOLS[tile_type]

    # Border drum herum legen (falls auto_boundary)
    if location.auto_boundary:
        boundary_tile = DEFAULT_BOUNDARIES.get(location.type)
        if boundary_tile is not None:
            boundary_symbol = TILE_SYMBOLS[boundary_tile]
            total_width = inner_width + 2
            border_row = [boundary_symbol] * total_width
            grid = (
                [list(border_row)]
                + [[boundary_symbol] + row + [boundary_symbol] for row in grid]
                + [list(border_row)]
            )

            # Ausgänge als Pfeile in den Border einzeichnen
            _apply_exits_to_border(grid, location.connections, inner_width, inner_height)

    # Grid zu String zusammenbauen
    lines = [" ".join(row) for row in grid]
    return "\n".join(lines)


def _get_target_name(target_id: str, world: World) -> str:
    """Gibt den Namen einer Ziel-Location zurück, oder die ID als Fallback"""
    target = world.get_location(target_id)
    return target.name if target else target_id


def display_location(location: Location, world: World) -> None:
    """Gibt eine Location mit Name, ASCII-Grid, Beschreibung und Verbindungen aus"""
    print(f"\n=== {location.name} ===")
    print(render_location(location))
    print(f"\n{location.description}")

    if not location.connections:
        return

    # Verbindungen gruppiert anzeigen:
    # Himmelsrichtungen (north/south/east/west) mit Pfeil
    # Alle anderen (Gebäude, Ausgänge) mit CONNECTION_SYMBOL
    direction_lines = []
    other_lines = []

    for key, target_id in location.connections.items():
        target_name = _get_target_name(target_id, world)
        if key in DIRECTION_SYMBOLS:
            direction_lines.append(f"  {DIRECTION_SYMBOLS[key]} {target_name} (go {target_id})")
        else:
            other_lines.append(f"  {CONNECTION_SYMBOL} {target_name} (go {target_id})")

    print("\nVerbindungen:")
    for line in direction_lines + other_lines:
        print(line)