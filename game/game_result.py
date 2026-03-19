from enum import StrEnum

class GameResult(StrEnum):
    """Rückgabewerte des Spielloops und der Befehlsverarbeitung"""
    CONTINUE = "continue"
    MENU = "menu"
    QUIT = "quit"