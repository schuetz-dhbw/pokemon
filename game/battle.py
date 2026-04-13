from game.context import GameContext
from models.pokemon.pokemon import Pokemon
from views.styles import info, important


def _choose_attack(pokemon: Pokemon) -> int | None:
    """Lässt den Spieler eine Attacke wählen. Gibt den Index zurück oder None bei Flucht."""
    print(f"\nWas möchtest du tun?")
    print("0. Fliehen")
    print(f"{pokemon.name}s Attacken:")
    for i, attack in enumerate(pokemon.attacks, 1):
        print(f"{i}. {attack.name} (Typ: {attack.type.value}, Schaden: {attack.power})")

    while True:
        choice = input("> ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(pokemon.attacks):
            return int(choice) - 1
        print(important(f"Bitte eine Zahl zwischen 0 und {len(pokemon.attacks)} eingeben."))


def run_battle(wild_pokemon: Pokemon, ctx: GameContext) -> None:
    """Führt einen einfachen Kampf gegen ein wildes Pokémon durch.
    Ein Angriff pro Seite, kein rundenbasierter Kampf (wird in Sprint 2 ausgebaut).

    Args:
        wild_pokemon: Das wilde Pokémon
        ctx: Zentraler Spielzustand
    """
    if not ctx.player.team:
        print("Du hast kein Pokémon dabei – du läufst schnell weg!")
        return

    player_pokemon = ctx.player.team[0]

    print(f"\n⚔️ {player_pokemon.name} (Level {player_pokemon.level}, HP: {player_pokemon.current_stats.hp}) "
          f"vs. {wild_pokemon.name} (Level {wild_pokemon.level}, HP: {wild_pokemon.current_stats.hp})")

    # Spielerzug: Attacke wählen
    attack_index = _choose_attack(player_pokemon)
    if attack_index is None:
        print("Du flieht aus dem Kampf!")
        return

    player_attack = player_pokemon.attacks[attack_index]
    wild_pokemon.current_stats.hp = max(0, wild_pokemon.current_stats.hp - player_attack.power)
    print(info(f"{player_pokemon.name} setzt {player_attack.name} ein! "
               f"{wild_pokemon.name} verliert {player_attack.power} HP."))

    if wild_pokemon.current_stats.hp <= 0:
        print(f"⭐ {wild_pokemon.name} wurde besiegt!")
        return

    print(f"  {wild_pokemon.name} hat noch {wild_pokemon.current_stats.hp} HP.")

    # Gegnerzug: erste Attacke des wilden Pokémon
    enemy_attack = wild_pokemon.attacks[0]
    player_pokemon.current_stats.hp = max(0, player_pokemon.current_stats.hp - enemy_attack.power)
    print(info(f"{wild_pokemon.name} setzt {enemy_attack.name} ein! "
               f"{player_pokemon.name} verliert {enemy_attack.power} HP."))

    if player_pokemon.current_stats.hp <= 0:
        print(important(f"{player_pokemon.name} wurde besiegt!"))
    else:
        print(f"  {player_pokemon.name} hat noch {player_pokemon.current_stats.hp} HP.")