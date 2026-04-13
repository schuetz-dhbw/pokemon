from game.dialogue import run_dialogue
from game.context import GameContext
from game.encounter import find_pokemon_in_zone, run_encounter
from game.game_result import GameResult
from models.world.location import Location
from models.world.tile import TileType, TILE_TO_HABITAT
from views.location_view import display_location
from views.styles import info

def _get_current_location(ctx: GameContext) -> Location | None:
    """Gibt die aktuelle Location zurück oder None bei Fehler"""
    location = ctx.world.get_location(ctx.player.current_location)
    if location is None:
        print("Fehler: Aktuelle Location nicht gefunden.")
    return location

def cmd_look(ctx: GameContext) -> None:
    """Zeigt die aktuelle Location als Karte mit Beschreibung"""
    location = _get_current_location(ctx)
    if location is None:
        return
    display_location(location, ctx)


def cmd_move(target_id: str, ctx: GameContext) -> None:
    """Bewegt den Spieler zu einer verbundenen Location
    """
    location = _get_current_location(ctx)
    if location is None:
        return

    # Ziel-ID ermitteln: erst als Key prüfen, dann als Value
    resolved_id = None
    if target_id in location.connections:
        resolved_id = location.connections[target_id]
    else:
        for value in location.connections.values():
            if value == target_id:
                resolved_id = value
                break

    if resolved_id is None:
        print(f"'{target_id}' ist von hier aus nicht erreichbar.")
        return

    # Zone zurücksetzen, falls Spieler eine Zone verlässt ohne 'leave'
    if ctx.player.current_zone is not None:
        ctx.player.current_zone = None
        ctx.player.previous_location = None

    target = ctx.world.get_location(resolved_id)
    if target is None:
        print(f"Fehler: Ziel-Location '{resolved_id}' nicht gefunden.")
        return

    ctx.player.current_location = resolved_id
    display_location(target, ctx)

def cmd_team(ctx: GameContext) -> None:
    """Zeigt alle Pokémon im Team des Spielers mit Typ und aktuellen HP"""
    if not ctx.player.team:
        print("Du hast noch keine Pokémon in deinem Team.")
        return
    print("\n=== Team ===")
    for pokemon in ctx.player.team:
        types = ", ".join(t.value for t in pokemon.types)
        print(f"  {pokemon.name} (Lv.{pokemon.level}) – {types} – HP: {pokemon.current_stats.hp}/{pokemon.base_stats.hp}")

def cmd_inventory(ctx: GameContext) -> None:
    """Zeigt das Inventar des Spielers"""
    if not ctx.player.inventory:
        print("Dein Inventar ist leer.")
        return

    print("\n=== Inventar ===")
    for item in ctx.player.inventory:
        print(f"  {item.quantity} x {item.name}")

def cmd_take(args: list[str], ctx: GameContext) -> None:
    """Nimmt Items aus der aktuellen Location ins Inventar"""
    if not args:
        print("Was möchtest du aufnehmen?")
        return

    location = _get_current_location(ctx)
    if location is None:
        return

    taken = []
    not_found = []

    for item_id in args:
        # Container können nicht direkt mitgenommen werden:
        # inspect öffnet sie und verschiebt ihren Inhalt in location.items --> danach ist Inhalt per take aufnehmbar
        container = next(
            (t for t in location.special_tiles
             if t["type"] == TileType.CONTAINER.value
             and t.get("name", "").lower() == item_id.lower()),
            None
        )
        if container:
            print(f"'{item_id}' kann nicht mitgenommen werden. Benutze 'inspect {item_id}'.")
            continue

        item_entry = next((i for i in location.items if i["item_id"] == item_id and not i.get("hidden")), None)
        if item_entry is None:
            not_found.append(item_id)
            continue

        item_def = ctx.items_db.get(item_id)
        if item_def is None:
            not_found.append(item_id)
            continue

        qty = item_entry.get("quantity", 1)

        # Ins Inventar
        existing = next((i for i in ctx.player.inventory if i.id == item_id), None)
        if existing:
            existing.quantity += qty
        else:
            ctx.player.inventory.append(item_def.copy(quantity=qty))

        location.items.remove(item_entry)
        taken.append(f"{qty}x {item_def.name}")

    if taken:
        print(info(f"Du hast aufgehoben: {', '.join(taken)}"))
    for item_id in not_found:
        print(f"'{item_id}' ist hier nicht zu finden.")

def cmd_inspect(name: str, ctx: GameContext) -> None:
    """Untersucht einen Container und macht seinen Inhalt aufnehmbar"""
    location = _get_current_location(ctx)
    if location is None:
        return

    container = next(
        (t for t in location.special_tiles
         if t["type"] == TileType.CONTAINER.value and t.get("name", "").lower() == name.lower()),
        None
    )
    if container is None:
        print(f"Hier gibt es kein '{name}'.")
        return

    desc = container.get("description", "")
    if desc:
        print(f"\n{desc}")

    items = container.get("items", [])
    if not items:
        print("Hier ist nichts zu finden.")
        return

    print("Darin befindet sich:")
    for item_entry in items:
        item_def = ctx.items_db.get(item_entry["item_id"])
        name_str = item_def.name if item_def else item_entry["item_id"]
        qty = item_entry.get("quantity", 1)
        print(f"  🎒 {qty}x {name_str} (take {item_entry['item_id']})")

    # Inhalt in location.items verschieben --> jetzt mit 'take' aufnehmbar
    location.items.extend(items)
    container["items"] = []

def cmd_talk(npc_id: str, ctx: GameContext) -> None:
    """Startet einen Dialog mit einem NPC in der aktuellen Location"""
    location = _get_current_location(ctx)
    if location is None:
        return
    if npc_id not in location.npcs:
        print(f"Hier ist niemand mit dem Namen '{npc_id}'.")
        return
    npc = ctx.npcs_db.get(npc_id)
    if npc is None:
        print(f"Fehler: NPC '{npc_id}' nicht in der Datenbank.")
        return
    run_dialogue(npc, ctx)

def cmd_walk(zone_type: TileType, ctx: GameContext) -> None:
    """Betritt eine Zone (z.B. hohes Gras) in der aktuellen Location.
    Prüft ob die Location Tiles des gewünschten Typs hat.
    Speichert die aktuelle Location für 'leave'.
    """
    location = _get_current_location(ctx)
    if location is None:
        return

    has_zone = any(
        TileType(t["type"]) == zone_type
        for t in location.special_tiles
    )
    if not has_zone:
        _print_available_zones(ctx)
        return

    ctx.player.current_zone = zone_type.value
    ctx.player.previous_location = ctx.player.current_location

    symbol = "🟩" if zone_type == TileType.GRASS else "🟦"
    border = symbol * 10
    print(f"\n{border}")
    print(f"Du betrittst das {zone_type.value}...")
    print(f"Hier könnten wilde Pokémon lauern (find).")
    print(border)


def cmd_leave(ctx: GameContext) -> None:
    """Verlässt die aktuelle Zone und kehrt zur vorherigen Location zurück."""
    if ctx.player.current_zone is None:
        print("Du befindest dich in keiner Zone.")
        return

    zone_name = ctx.player.current_zone
    ctx.player.current_zone = None

    if ctx.player.previous_location:
        ctx.player.current_location = ctx.player.previous_location
        ctx.player.previous_location = None

    print(f"Du verlässt das {zone_name.lower()}.")
    location = _get_current_location(ctx)
    if location:
        display_location(location, ctx)


def cmd_find(ctx: GameContext) -> None:
    """Sucht nach wilden Pokémon in der aktuellen Zone."""
    if ctx.player.current_zone is None:
        print("Du befindest dich in keiner Zone. Betritt zuerst hohes Gras (walk gras).")
        return

    zone_type = TileType(ctx.player.current_zone)
    habitat = TILE_TO_HABITAT.get(zone_type)

    if habitat is None:
        print(f"In dieser Zone gibt es keine wilden Pokémon.")
        return

    pokemon = find_pokemon_in_zone(habitat, ctx)

    if pokemon is None:
        print("Du durchsuchst das Gras... aber hier ist im Moment kein wildes Pokémon.")
        return

    run_encounter(pokemon, ctx)

def _print_available_zones(ctx: GameContext) -> None:
    """Gibt die betretbaren Zonen der aktuellen Location aus"""
    location = _get_current_location(ctx)
    if location is None:
        return
    zones = {
        TileType(t["type"])
        for t in location.special_tiles
        if TileType(t["type"]) in TILE_TO_HABITAT
    }
    if zones:
        zone_names = ", ".join(f"'{z.value.lower()}'" for z in zones)
        print(f"Verfügbare Zonen hier: {zone_names} (z.B. 'walk gras')")
    else:
        print("Hier gibt es keine betretbaren Zonen.")

def cmd_npcs(ctx: GameContext) -> None:
    """Listet alle NPCs in der aktuellen Location auf"""
    location = _get_current_location(ctx)
    if location is None or not location.npcs:
        print("Hier ist niemand.")
        return
    print("\nPersonen hier:")
    for npc_id in location.npcs:
        npc = ctx.npcs_db.get(npc_id)
        name = npc.name if npc else npc_id
        desc = f" – {npc.description}" if npc and npc.description else ""
        print(f"  {name} (talk {npc_id}){desc}")


def parse_command(
    raw_input: str,
    ctx: GameContext,
    save_callback,
    load_callback
) -> GameResult:
    """Parst und führt einen Befehl aus

    Args:
        raw_input: Rohe Eingabe des Spielers
        ctx: GameContext enthält alle relevanten Spieldaten
        save_callback: Funktion zum Speichern des Spielstands
        load_callback: Funktion zum Laden des Spielstands

    Returns:
        "continue" - Spielloop weiterführen
        "menu"     - Zurück ins Hauptmenü
        "quit"     - Spiel beenden
    """
    parts = raw_input.strip().lower().split()
    if not parts:
        return GameResult.CONTINUE

    command = parts[0]
    args = parts[1:]

    match command:
        case "look" | "schau":
            cmd_look(ctx)

        case "go" | "gehe":
            if args:
                cmd_move(args[0], ctx)
            else:
                print("Wohin möchtest du gehen? Tippe 'look' um Verbindungen zu sehen.")

        case "talk" | "rede":
            if args:
                cmd_talk(args[0], ctx)
            else:
                cmd_npcs(ctx)

        case "team":
            cmd_team(ctx)

        case "inventory" | "inventar" | "inv":
            cmd_inventory(ctx)

        case "take" | "nimm":
            cmd_take(args, ctx)

        case "inspect" | "untersuche":
            if args:
                cmd_inspect(" ".join(args), ctx)
            else:
                print("Was möchtest du untersuchen?")

        case "walk" | "betrete":
            if not args:
                print("Welche Zone möchtest du betreten? (z.B. 'walk gras')")
            else:
                zone_name = " ".join(args).capitalize()
                try:
                    zone_type = TileType(zone_name)
                    if zone_type not in TILE_TO_HABITAT:
                        print(f"'{zone_name}' ist keine betretbare Zone.")
                    else:
                        cmd_walk(zone_type, ctx)
                except ValueError:
                    _print_available_zones(ctx)

        case "leave" | "verlasse":
            cmd_leave(ctx)

        case "find":
            cmd_find(ctx)

        case "save" | "speichern":
            save_name = args[0] if args else "savegame"
            save_callback(save_name)

        case "load" | "laden":
            save_name = args[0] if args else "savegame"
            load_callback(save_name)

        case "menu" | "hauptmenu":
            print("Zurück ins Hauptmenü ...")
            return GameResult.MENU

        case "help" | "hilfe" | "?":
            print_help()

        case "quit" | "beenden":
            print("Bis zum nächsten Mal!")
            return GameResult.QUIT

        case _:
            print(f"Unbekannter Befehl: '{command}'. Tippe 'hilfe' für eine Übersicht.")

    return GameResult.CONTINUE


def print_help() -> None:
    """Gibt eine Übersicht aller verfügbaren Befehle aus"""
    print("\n=== Befehle ===")
    print("  look / schau                  - Aktuelle Location anzeigen")
    print("  go / gehe <ziel>              - Zu einer Location navigieren (z.B. 'go route_01')")
    print("  talk / rede <npc>             - Mit einem NPC sprechen (z.B. 'talk mom')")
    print("  team                          - Team anzeigen")
    print("  inventory / inventar / inv    - Inventar anzeigen")
    print("  take / nimm <item>            - Item aufnehmen (mehrere: 'take pokeball heiltrank')")
    print("  inspect / untersuche <objekt> - Objekt untersuchen")
    print("  walk / betrete <zone>         - Zone betreten (z.B. 'walk gras')")
    print("  find                          - Nach wilden Pokémon suchen (nur in Zone)")
    print("  leave / verlasse              - Zone verlassen")
    print("  save / speichern [name]       - Spielstand speichern")
    print("  load / laden [name]           - Spielstand laden")
    print("  menu / hauptmenu              - Hauptmenu aufrufen")
    print("  help / hilfe / ?              - Diese Übersicht")
    print("  quit / beenden                - Spiel beenden")