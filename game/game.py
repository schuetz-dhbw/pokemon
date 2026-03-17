from game.commands import parse_command
from game.context import GameContext
from models.characters.player import Player
from models.item import Item, ItemType
from utils.data_loader import DataLoader
from utils.save_manager import SaveManager
from views.location_view import display_location


class Game:
    """Verwaltet den Spielzustand und den Hauptloop"""

    def __init__(self, data_dir: str = "data", saves_dir: str = "saves"):
        self.loader = DataLoader(data_dir=data_dir)
        self.save_manager = SaveManager(saves_dir=saves_dir)
        self.context: GameContext | None = None

    def _build_context(self, player, world, pokemons_db, items_db, npcs_db) -> GameContext:
        return GameContext(
            player=player,
            world=world,
            npcs_db=npcs_db,
            items_db=items_db,
            pokemons_db=pokemons_db
        )

    def new_game(self, player_name: str) -> None:
        """Startet ein neues Spiel"""
        world, pokemons_db, items_db, npcs_db = self.loader.load_all()
        starter_pokeball = Item(id="pokeball", name="Pokéball", type=ItemType.BALL, quantity=5)
        player = Player(
            name=player_name,
            current_location=world.starting_location,
            inventory=[starter_pokeball]
        )

        self.context = self._build_context(player, world, pokemons_db, items_db, npcs_db)

        print(f"\nWillkommen, {player_name}! Dein Abenteuer beginnt!")
        print("Tippe 'hilfe' für eine Übersicht der Befehle.")

        start = world.get_location(world.starting_location)
        if start:
            display_location(start, self.context)

    def load_game(self, save_name: str) -> None:
        """Lädt einen Spielstand"""
        try:
            player, world, npcs_db = self.save_manager.load_game(save_name, self.loader)
            _, pokemons_db, items_db, _ = self.loader.load_all()
            self.context = self._build_context(player, world, pokemons_db, items_db, npcs_db)
            print(f"Spielstand '{save_name}' geladen.")
        except FileNotFoundError:
            print(f"Kein Spielstand '{save_name}' gefunden.")

    def save_game(self, save_name: str) -> None:
        """Speichert den aktuellen Spielstand"""
        if self.context is None:
            print("Kein aktives Spiel zum Speichern.")
            return
        self.save_manager.save_game(self.context, save_name)

    def run(self) -> str:
        """Spielloop - läuft bis der Spieler quit oder menu eingibt.

        Returns:
            "quit" wenn das Spiel beendet werden soll
            "menu" wenn ins Hauptmenü zurückgekehrt werden soll
        """
        if self.context is None:
            print("Fehler: Spiel nicht initialisiert.")
            return "quit"

        while True:
            try:
                raw_input = input(f"\n[{self.context.player.name}] > ")
                result = parse_command(
                    raw_input,
                    self.context,
                    save_callback=self.save_game,
                    load_callback=self.load_game
                )
                if result in ("quit", "menu"):
                    return result
            except KeyboardInterrupt:
                print("\nSpiel unterbrochen.")
                return "quit"

    def main_menu(self) -> None:
        """Hauptmenü-Loop - läuft bis das Spiel beendet wird"""
        while True:
            saves = self.save_manager.list_saves()

            print("\n=== Hauptmenü ===")
            print("1 - Neues Spiel")
            if saves:
                print("2 - Spielstand laden")

            choice = input("> ").strip()

            match choice:
                case "2" if saves:
                    print("\nVerfügbare Spielstände:")
                    for i, (save_name, label) in enumerate(saves, 1):
                        print(f"  {i}. {label}")

                    save_input = input("\nName oder Nummer: ").strip()
                    if save_input.isdigit() and 1 <= int(save_input) <= len(saves):
                        save_name = saves[int(save_input) - 1][0]
                    else:
                        save_name = save_input or "savegame"

                    self.load_game(save_name)

                case _:
                    player_name = input("Wie lautet dein Name, Trainer?\n> ").strip()
                    self.new_game(player_name)

            result = self.run()
            if result == "quit":
                break
            # result == "menu" -> Schleife läuft weiter, Hauptmenü wird erneut angezeigt