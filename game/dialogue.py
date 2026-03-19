from game.context import GameContext
from models.characters.npc import NPC
from utils import DataLoader
from views.styles import info, important

_NODE_END = "end"
_NODE_START = "start"
# action["type"] und condition["type"] currently not typesafe (plain string)
# might be improved ...

def _find_node(npc: NPC, node_id: str) -> dict | None:
    return next((n for n in npc.dialogue if n["id"] == node_id), None)


def _execute_action(action: dict, npc: NPC, ctx: GameContext) -> None:
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
            existing = next((i for i in ctx.player.inventory if i.id == item_id), None)
            if existing:
                existing.quantity += npc_item.quantity
            else:
                ctx.player.inventory.append(npc_item.copy())
            npc_item.quantity = 0
            print(info(f"Du hast {npc_item.name} erhalten!"))

        case "heal_team":
            for pokemon in ctx.player.team:
                pokemon.current_stats.hp = pokemon.base_stats.hp
            if ctx.player.team:
                print(info("Deine Pokémon wurden vollständig geheilt!"))

        case "give_pokemon":
            pokemon_id = action["pokemon_id"]
            if len(ctx.player.team) >= 6:
                print(important("Dein Team ist voll! Du kannst kein weiteres Pokémon aufnehmen."))
                return
            poke_data = ctx.pokemons_db.get(pokemon_id)
            if poke_data is None:
                print(important(f"[Fehler: Pokémon {pokemon_id} nicht in DB]"))
                return
            pokemon = DataLoader.create_pokemon_from_data(poke_data)
            ctx.player.team.append(pokemon)
            print(info(f"Du hast {pokemon.name} erhalten!"))

def _check_condition(condition: dict, ctx: GameContext) -> bool:
    """Prüft ob die Voraussetzung für eine Aktion gegeben ist.

    Unterstützte Checks:
    - has_pokemons:      Player hat mind. ein Pokémon im Team
    - has_pokemon:       Player hat ein bestimmtes Pokémon im Team
    - has_item:          Player hat ein bestimmtes Item im Inventar
    """
    match condition["type"]:
        case "has_pokemons":
            return len(ctx.player.team) > 0
        case "has_pokemon":
            return any(i.id == condition["pokemon_id"] for i in ctx.player.team)
        case "has_item":
            return any(i.id == condition["item_id"] for i in ctx.player.inventory)
        case _:
            return True

def run_dialogue(npc: NPC, ctx: GameContext) -> None:
    if not npc.dialogue:
        print(f"{npc.name}: ...")
        return

    start_id = npc.current_node
    node = _find_node(npc, start_id)
    if node is None:
        node = _find_node(npc, _NODE_START)  # Fallback

    if node is None:
        print(f"{npc.name}: ...")
        return

    while node is not None and node["id"] != _NODE_END:
        text = node["text"].format(player_name=ctx.player.name)
        print(f"\n{npc.name}:\n{text}")

        if "choices" not in node:
            input("[Enter drücken um fortzufahren]")

        if "action" in node:
            _execute_action(node["action"], npc, ctx)

        if "auto_branch" in node:
            next_id = None
            for branch in node["auto_branch"]:
                if "condition" not in branch or _check_condition(branch["condition"], ctx):
                    next_id = branch["next"]
                    break
            node = _find_node(npc, next_id) if next_id and next_id != _NODE_END else None
            continue

        if "next_start" in node:
            npc.current_node = node["next_start"]

        if "choices" in node:
            choices = node["choices"]
            options = " / ".join(f"[{c['answer']}]" for c in choices)
            print(f"{options}")
            while True:
                answer = input("> ").strip().lower()
                match = next((c for c in choices if c["answer"].lower() == answer), None)
                if match:
                    if "condition" in match and not _check_condition(match["condition"], ctx):
                        print(important("Diese Option steht dir gerade nicht zur Verfügung."))
                        continue
                    if "action" in match:
                        _execute_action(match["action"], npc, ctx)
                    node = _find_node(npc, match["next"])
                    break
                print(important(f"Bitte antworte mit: {options}"))

        elif "next" in node:
            next_id = node["next"]
            if next_id == _NODE_END:
                break
            node = _find_node(npc, next_id)
        else:
            break