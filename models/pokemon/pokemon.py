from dataclasses import dataclass
from typing import List

from models.pokemon.attack import Attack
from models.pokemon.pokemon_type import PokemonType
from models.pokemon.stats import Stats
from models.world.tile import HabitatType

@dataclass
class Pokemon:
    """ Beschreibt ein Pokemon mit seinen Stats, Attacken und Eigenschaften """
    id: int
    name: str
    types: List[PokemonType]

    # Stats
    base_stats: Stats
    current_stats: Stats
    level: int

    # Kampf
    attacks: List[Attack]

    # Welt & Fangen
    habitats: List[HabitatType]
    catch_rate: int
    spawn_probability: float