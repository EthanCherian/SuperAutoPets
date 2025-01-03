from utils.helpers import debug, red, yellow, green
from objects import pets
from objects.team import Team

def battle(team1: Team, team2: Team):
    winner = ""
    print("\n_______________BATTLE STARTING_______________")
    team1.full_info()
    print("                      VS ")
    team2.full_info()
    print()

    input("Press \'Enter\' to continue...")
    print()

    team1.on_battle_start(team2)
    team2.on_battle_start(team1)

    while len(team1.battle_pets) > 0 and len(team2.battle_pets) > 0:
        debug("")

        pet1 = team1.battle_pets[0]
        pet2 = team2.battle_pets[0]
        debug(f"  {pet1}   vs   {pet2}")
        debug(f"{pet1.get_battle_stats()} vs {pet2.get_battle_stats()}")

        team1.battle_turn(team2)
        debug("")

        team1.battle_info()
        print("                      VS ")
        team2.battle_info()

        input("Press \'Enter\' to continue...")
        debug("")

    if len(team1.battle_pets) > 0:
        green(f" Team {team1.name} wins! ")
        winner = team1.name
        team1.print()
    elif len(team2.battle_pets) > 0:
        green(f" Team {team2.name} wins! ")
        winner = team2.name
        team2.print()
    else:
        green(" It's a draw! ")

    debug("")

    team1.reset()
    team2.reset()

    return winner
