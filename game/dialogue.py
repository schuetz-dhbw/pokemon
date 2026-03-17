from models.characters.npc import NPC
from models.characters.player import Player
from views.styles import info


def _find_node(npc: NPC, node_id: str) -> dict | None:
    return next((n for n in npc.dialogue if n["id"] == node_id), None)


def _execute_action(action: dict, npc: NPC, player: Player) -> None:
    """Führt eine Dialogue-Aktion aus.

    Unterstützte Aktionen:
    - give_item:         NPC übergibt Item aus seinem Inventar an den Spieler
    - heal_team:         NPC heilt das gesamte Team des Spielers

    Beispiele für zukünftige weitere Aktionen:
    start_battle (Kampf gegen Trainer starten) oder unlock_connection (gesperrte Route zugänglich machen)
    """
    match action["type"]:
        case "give_item":
            item_id = action["item_id"]
            npc_item = next((i for i in npc.inventory if i.id == item_id), None)
            if npc_item is None or npc_item.quantity <= 0:
                return
            existing = next((i for i in player.inventory if i.id == item_id), None)
            if existing:
                existing.quantity += npc_item.quantity
            else:
                player.inventory.append(npc_item)
            npc_item.quantity = 0
            print(info(f"Du hast {npc_item.name} erhalten!"))

        case "heal_team":
            for pokemon in player.team:
                pokemon.current_stats.hp = pokemon.base_stats.hp
            if player.team:
                print(info("Deine Pokémon wurden vollständig geheilt!"))

        case "give_pokemon":
            pokemon_id = action["pokemon_id"]
            npc.visited = True
            # Platzhalter – wird nach GameContext-Umbau implementiert
            print(info(f"[Pokemon {pokemon_id} erhalten – noch nicht implementiert]"))

def run_dialogue(npc: NPC, player: Player) -> None:
    if not npc.dialogue:
        print(f"{npc.name}: ...")
        return

    # visited-Knoten überschreibt start, falls vorhanden
    start_id = "visited" if npc.visited else "start"
    node = _find_node(npc, start_id)
    if node is None:
        node = _find_node(npc, "start")  # Fallback

    if node is None:
        print(f"{npc.name}: ...")
        return

    while node is not None and node["id"] != "end":
        text = node["text"].format(player_name=player.name)
        print(f"\n{npc.name}:\n{text}")

        if "choices" not in node:
            input("[Enter drücken um fortzufahren]")

        if "action" in node:
            _execute_action(node["action"], npc, player)

        if "choices" in node:
            choices = node["choices"]
            options = " / ".join(f"[{c['answer']}]" for c in choices)
            print(f"{options}")
            while True:
                answer = input("> ").strip().lower()
                match = next((c for c in choices if c["answer"].lower() == answer), None)
                if match:
                    if "action" in match:
                        _execute_action(match["action"], npc, player)
                    node = _find_node(npc, match["next"])
                    break
                print(important(f"Bitte antworte mit: {options}"))

        elif "next" in node:
            next_id = node["next"]
            if next_id == "end":
                break
            node = _find_node(npc, next_id)
        else:
            break

    npc.visited = True
    npc.current_node = "start"