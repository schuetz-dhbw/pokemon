from dataclasses import dataclass

from models.characters.character import Character


@dataclass
class Player(Character):
    """ Spieler-Charakter mit aktueller Position, Geld und Bewegungsgeschwindigkeit """
    current_location: str = "city_alabastia"
    current_zone: str | None = None        # aktive Zone (z.B. "Gras"), None = in der Location
    previous_location: str | None = None  # Location vor Zonen-Eintritt, für 'leave'
    money: int = 300