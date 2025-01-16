from utils.helpers import blue
from tasks.game import Game
from tasks.info import Info

blue("** Welcome to Super Auto Pets! **")
team_name = input("Enter a team name: ")

team_export = input("Would you like to backup your teams to a file for later use? (y/n): ").lower() == "y"
if team_export:
    blue("\tYour team will be saved after each round.")

info_display = input("If you'd like to see info on pets, abilities, and foods, type \'info\'. Otherwise, press \'Enter\' to begin the game... ").lower() == "info"
if info_display:
    Info().display()
blue("Starting game... Good luck!")
input("Press \'Enter\' to continue...")
game = Game(team_name, team_export)
game.play()