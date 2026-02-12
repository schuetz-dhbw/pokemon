from models.characters.player import Player
from models.world.world import World
from views.location_view import display_location


def cmd_look(player: Player, world: World) -> None:
    """Zeigt die aktuelle Location als Karte mit Beschreibung"""
    location = world.get_location(player.current_location)
    if location is None:
        print("Fehler: Aktuelle Location nicht gefunden.")
        return
    display_location(location, world)


def cmd_move(target_id: str, player: Player, world: World) -> None:
    """Bewegt den Spieler zu einer verbundenen Location

    Args:
        target_id: ID der Ziel-Location (Connection-Key oder Ziel-ID)
        player: Spieler-Objekt
        world: Welt-Objekt
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
    display_location(target, world)


def cmd_inventory(player: Player) -> None:
    """Zeigt das Inventar des Spielers"""
    if not player.inventory:
        print("Dein Inventar ist leer.")
        return

    print("\n=== Inventar ===")
    for item in player.inventory:
        print(f"  {item.quantity} x {item.name}")


def parse_command(
    raw_input: str,
    player: Player,
    world: World,
    save_callback,
    load_callback
) -> str:
    """Parst und führt einen Befehl aus

    Args:
        raw_input: Rohe Eingabe des Spielers
        player: Spieler-Objekt
        world: Welt-Objekt
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
            cmd_look(player, world)

        case "go" | "gehe":
            if args:
                cmd_move(args[0], player, world)
            else:
                print("Wohin möchtest du gehen? Tippe 'look' um Verbindungen zu sehen.")

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
    print("  inventory / inventar / inv    - Inventar anzeigen")
    print("  save / speichern [name]       - Spielstand speichern")
    print("  load / laden [name]           - Spielstand laden")
    print("  help / hilfe / ?              - Diese Übersicht")
    print("  quit / beenden                - Spiel beenden")