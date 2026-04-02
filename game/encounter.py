import random

from game.context import GameContext
from models.pokemon.pokemon import Pokemon
from models.world.tile import HabitatType
from utils.data_loader import DataLoader


def find_pokemon_in_zone(habitat: HabitatType, ctx: GameContext) -> Pokemon | None:
    """Sucht ein zufälliges wildes Pokémon im angegebenen Habitat.

    Für jedes Pokémon mit passendem Habitat wird ein Münzwurf mit seiner spawn_probability durchgeführt.
    Bei mehreren Treffern wird zufällig eines ausgewählt.

    Args:
        habitat: Das aktuelle Habitat (Zone) des Spielers
        ctx: Zentraler Spielzustand

    Returns:
        Pokemon-Instanz oder None wenn kein Pokémon gefunden
    """
    candidates = []

    for poke_data in ctx.pokemons_db.values():
        habitats = poke_data.get("habitat", [])
        if habitat.value not in habitats:
            continue

        spawn_probability = poke_data.get("spawn_probability", 0)
        roll = random.random()
        hit = roll < spawn_probability

        if hit:
            candidates.append(poke_data)

    if not candidates:
        return None

    found = random.choice(candidates)
    return DataLoader.create_pokemon_from_data(found)


def run_encounter(pokemon: Pokemon, ctx: GameContext) -> None:
    """Führt eine wilde Pokémon-Begegnung durch.

    Args:
        pokemon: Das wild erschienene Pokémon
        ctx: Zentraler Spielzustand
    """
    print(f"\n⚡ Ein wildes {pokemon.name} (Lv.{pokemon.level}) taucht auf!")

    if not ctx.player.team:
        print("Du hast kein Pokémon dabei – du läufst weg!")
        return

    answer = input("Möchtest du kämpfen? [ja/nein] > ").strip().lower()
    if answer != "ja":
        print("Du weichst dem wilden Pokémon aus.")
        return

    # TODO: Kampflogik hier einfügen
    # Aktuell: Spieler kehrt einfach in die Zone zurück
    print("(Kampf noch nicht implementiert – du kehrst ins Gras zurück.)")
