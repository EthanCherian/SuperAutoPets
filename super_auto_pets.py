from game import Game

print("** Welcome to Super Auto Pets! **")
team_name = input("Enter a team name: ")

team_export = input("Would you like to backup your teams to a file for later use? (y/n): ").lower() == "y"

game = Game(team_name, team_export)
game.play()