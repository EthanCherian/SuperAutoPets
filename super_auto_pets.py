from game import Game

print("** Welcome to Super Auto Pets! **")
name = input("Enter a team name: ")

export = input("Would you like to backup your teams to a file for later use? (y/n): ").lower() == "y"

game = Game(name, export)
game.play()