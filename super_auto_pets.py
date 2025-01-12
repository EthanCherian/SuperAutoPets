from utils.helpers import blue
from tasks.game import Game

blue("** Welcome to Super Auto Pets! **")
team_name = input("Enter a team name: ")

team_export = input("Would you like to backup your teams to a file for later use? (y/n): ").lower() == "y"

info_display = input("If you'd like to see info on pets, type \'info\'. Otherwise, press \'Enter\' to begin the game...").lower() == "info"

game = Game(team_name, team_export)
game.play()