from game.dialogue import run_dialogue
from models.characters.npc import NPC
from models.characters.player import Player
from models.world.world import World
from views.location_view import display_location


def cmd_look(player: Player, world: World, npcs_db: dict[str, NPC]) -> None:
    """Zeigt die aktuelle Location als Karte mit Beschreibung"""
    location = world.get_location(player.current_location)
    if location is None:
        print("Fehler: Aktuelle Location nicht gefunden.")
        return
    display_location(location, world, npcs_db)


def cmd_move(target_id: str, player: Player, world: World, npcs_db: dict[str, NPC]) -> None:
    """Bewegt den Spieler zu einer verbundenen Location
    """
    location = world.get_location(player.current_location)
    if location is None:
        print("Fehler: Aktuelle Location nicht gefunden.")
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

    target = world.get_location(resolved_id)
    if target is None:
        print(f"Fehler: Ziel-Location '{resolved_id}' nicht gefunden.")
        return

    player.current_location = resolved_id
    display_location(target, world, npcs_db)


def cmd_inventory(player: Player) -> None:
    """Zeigt das Inventar des Spielers"""
    if not player.inventory:
        print("Dein Inventar ist leer.")
        return

    print("\n=== Inventar ===")
    for item in player.inventory:
        print(f"  {item.quantity} x {item.name}")


def cmd_talk(npc_id: str, player: Player, world: World, npcs_db: dict[str, NPC]) -> None:
    """Startet einen Dialog mit einem NPC in der aktuellen Location"""
    location = world.get_location(player.current_location)
    if location is None:
        print("Fehler: Aktuelle Location nicht gefunden.")
        return
    if npc_id not in location.npcs:
        print(f"Hier ist niemand mit dem Namen '{npc_id}'.")
        return
    npc = npcs_db.get(npc_id)
    if npc is None:
        print(f"Fehler: NPC '{npc_id}' nicht in der Datenbank.")
        return
    run_dialogue(npc, player)


def cmd_npcs(player: Player, world: World, npcs_db: dict[str, NPC]) -> None:
    """Listet alle NPCs in der aktuellen Location auf"""
    location = world.get_location(player.current_location)
    if location is None or not location.npcs:
        print("Hier ist niemand.")
        return
    print("\nPersonen hier:")
    for npc_id in location.npcs:
        npc = npcs_db.get(npc_id)
        name = npc.name if npc else npc_id
        desc = f" – {npc.description}" if npc and npc.description else ""
        print(f"  {name} (talk {npc_id}){desc}")


def parse_command(
    raw_input: str,
    player: Player,
    world: World,
    npcs_db: dict[str, NPC],
    save_callback,
    load_callback
) -> str:
    """Parst und führt einen Befehl aus

    Args:
        raw_input: Rohe Eingabe des Spielers
        player: Spieler-Objekt
        world: Welt-Objekt
        npcs_db: Dict aller geladenen NPC-Objekte
        save_callback: Funktion zum Speichern des Spielstands
        load_callback: Funktion zum Laden des Spielstands

    Returns:
        "continue" - Spielloop weiterführen
        "menu"     - Zurück ins Hauptmenü
        "quit"     - Spiel beenden
    """
    parts = raw_input.strip().lower().split()
    if not parts:
        return "continue"

    command = parts[0]
    args = parts[1:]

    match command:
        case "look" | "schau":
            cmd_look(player, world, npcs_db)

        case "go" | "gehe":
            if args:
                cmd_move(args[0], player, world, npcs_db)
            else:
                print("Wohin möchtest du gehen? Tippe 'look' um Verbindungen zu sehen.")

        case "talk" | "rede":
            if args:
                cmd_talk(args[0], player, world, npcs_db)
            else:
                cmd_npcs(player, world, npcs_db)

        case "inventory" | "inventar" | "inv":
            cmd_inventory(player)

        case "save" | "speichern":
            save_name = args[0] if args else "savegame"
            save_callback(save_name)

        case "load" | "laden":
            save_name = args[0] if args else "savegame"
            load_callback(save_name)

        case "menu" | "hauptmenu":
            print("Zurück ins Hauptmenü ...")
            return "menu"

        case "help" | "hilfe" | "?":
            print_help()

        case "quit" | "beenden":
            print("Bis zum nächsten Mal!")
            return "quit"

        case _:
            print(f"Unbekannter Befehl: '{command}'. Tippe 'hilfe' für eine Übersicht.")

    return "continue"


def print_help() -> None:
    """Gibt eine Übersicht aller verfügbaren Befehle aus"""
    print("\n=== Befehle ===")
    print("  look / schau                  - Aktuelle Location anzeigen")
    print("  go / gehe <ziel>              - Zu einer Location navigieren (z.B. 'go route_01')")
    print("  talk / rede <npc>             - Mit einem NPC sprechen (z.B. 'talk mom')")
    print("  talk / rede                   - Alle NPCs in der Location anzeigen")
    print("  inventory / inventar / inv    - Inventar anzeigen")
    print("  save / speichern [name]       - Spielstand speichern")
    print("  load / laden [name]           - Spielstand laden")
    print("  menu / hauptmenu              - Hauptmenu aufrufen")
    print("  help / hilfe / ?              - Diese Übersicht")
    print("  quit / beenden                - Spiel beenden")