from dataclasses import dataclass
from enum import Enum

from models.pokemon.pokemon_type import PokemonType

class AttackCategory(Enum):
    PHYSICAL = "Physisch"
    STATUS = "Status"
    SPECIAL = "Spezial"

class StatusEffectType(Enum):
    POISON = "Vergiftung"
    BURN = "Verbrennung"
    STAT_CHANGE = "Statusveränderung"

@dataclass
class StatusEffect:
    """ Beschreibt einen Status-Effekt, der durch eine Attacke ausgelöst werden kann """
    effect_type: StatusEffectType
    chance: float # z.B. 0.3 - Wahrscheinlichkeit, dass Effekt eintritt
    target_stat: str | None = None # z.B. "attack" oder "defense" - bestimmt welcher Stat beeinflusst wird
    change: int | None = None # z.B. +1 oder -1 - bestimmt, um wie viel der Stat verändert wird
    duration: int | None = None # z.B. 3 Runden Vergiftung - bestimmt wie lange ein Stat beeinflusst wird

@dataclass
class Attack:
    """ Beschreibt eine Attacke, die im Kampf eingesetzt werden kann """
    name: str
    type: PokemonType # Art der Attacke entspricht in Gen1 den Pokemon-Typen
    power: int
    accuracy: float
    category: AttackCategory
    required_level: int
    status_effect: StatusEffect | None = None