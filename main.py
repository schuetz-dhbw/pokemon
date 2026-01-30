import intro

intro.play_intro()

while True:
    print("Prof. Eich:\nHallo! Schön dich kennenzulernen!\nWillkommen in der Welt der Pokémon!\nMein Name ist Eich. Aber alle nennen mich Pokémon-Professor.")
    player_name = input("Prof. Eich:\nWie ist dein Name?\nSpieler:\n")
    print("Prof. Eich:\nSchön. Hallo " + player_name + "!")
    break