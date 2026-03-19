from game.dialogue import run_dialogue
from game.context import GameContext
from game.game_result import GameResult
from models.world.tile import TileType
from views.location_view import display_location
from views.styles import info

def _get_current_location(ctx: GameContext):
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

    target = ctx.world.get_location(resolved_id)
    if target is None:
        print(f"Fehler: Ziel-Location '{resolved_id}' nicht gefunden.")
        return

    ctx.player.current_location = resolved_id
    display_location(target, ctx)

def cmd_team(ctx: GameContext) -> None:
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
        container = next(
            (t for t in location.special_tiles
             if t["type"] == TileType.CONTAINER.value
             and t.get("name", "").lower() == item_id.lower()),
            None
        )
        if container:
            print(f"'{item_id}' kann nicht mitgenommen werden.")
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

    # Inhalt in location.items verschieben → jetzt mit take aufnehmbar
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
    print("  save / speichern [name]       - Spielstand speichern")
    print("  load / laden [name]           - Spielstand laden")
    print("  menu / hauptmenu              - Hauptmenu aufrufen")
    print("  help / hilfe / ?              - Diese Übersicht")
    print("  quit / beenden                - Spiel beenden")