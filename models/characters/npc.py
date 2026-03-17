from dataclasses import dataclass, field
from typing import List
from enum import Enum

from models.characters.character import Character

class NPCType(Enum):
    TRAINER = "Trainer"
    SHOPKEEPER = "Händler"
    QUEST_GIVER = "Questgeber"
    HEALER = "Heiler"

@dataclass
class NPC(Character):
    """ Non-Player-Character mit spezifischem Typ und Dialogen """
    npc_type: NPCType = NPCType.TRAINER
    description: str = "" # Beschreibung für look / inspect
    dialogue: List[dict] = field(default_factory=list)  # Dialogue-Tree (Liste von Knoten)
    current_node: str = "start"  # Aktueller Knoten im Dialogue-Tree