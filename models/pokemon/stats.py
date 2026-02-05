from dataclasses import dataclass

@dataclass
class Stats:
    """ Kampfwerte eines Pokemons """
    hp: int
    attack: int
    defense: int
    initiative: int