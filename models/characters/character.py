from dataclasses import dataclass, field

from models.item import Item
from models.pokemon.pokemon import Pokemon

@dataclass
class Character:
    """ Basis-Klasse für Spieler und NPCs mit Team und Inventar """
    name: str # eindeutiger Name
    team: list[Pokemon] = field(default_factory=list) # max. 6 Stück
    inventory: list[Item] = field(default_factory=list)