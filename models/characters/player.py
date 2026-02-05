from dataclasses import dataclass

from models.characters.character import Character


@dataclass
class Player(Character):
    """ Spieler-Charakter mit aktueller Position, Geld und Bewegungsgeschwindigkeit """
    current_location: str = "city_alabastia"
    money: int = 300
    movement_speed: int = 1