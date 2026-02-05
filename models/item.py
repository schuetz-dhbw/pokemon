from dataclasses import dataclass
from enum import Enum

class ItemType(Enum):
    BALL = "Ball" # Zum Fangen --> Verbrauchen sich beim Fangversuch
    POTION = "Trank" # gegen Gift oder für mehr HP --> Ändern Status, sind danach weg
    KEY_ITEM = "Schlüsselitem" # z.B. Fahrrad --> Muss man haben, um sie zu nutzen, aber verbrauchen sich nicht

@dataclass
class Item:
    """ Item, das der Spieler im Inventar haben und nutzen kann """
    id: str
    name: str
    type: ItemType
    heal_hp: int | None = None
    quantity: int = 1