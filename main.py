from views.intro import play_intro
from game.game import Game

play_intro()

game = Game(data_dir="data", saves_dir="saves")
game.main_menu()