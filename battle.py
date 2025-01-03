from utils.helpers import debug, error, warning, success
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
        success(f" Team {team1.name} wins! ")
        winner = team1.name
        team1.print()
    elif len(team2.battle_pets) > 0:
        success(f" Team {team2.name} wins! ")
        winner = team2.name
        team2.print()
    else:
        success(" It's a draw! ")

    debug("")

    team1.reset()
    team2.reset()

    return winner

team1 = Team("1")
team1.add_pet(pets.GET_PET("camel"), 0)
parrot = pets.GET_PET("parrot")
parrot.receive_perk(7)
team1.add_pet(parrot, 1)
team1.add_pet(pets.GET_PET("rat"), 2)



team2 = Team("2")
team2.add_pet(pets.GET_PET("scorpion"), 0)
team2.add_pet(pets.GET_PET("cricket"), 1)
team2.add_pet(pets.GET_PET("sheep"), 2)
team2.add_pet(pets.GET_PET("dog"), 3)
team2.add_pet(pets.GET_PET("horse"), 4)

battle(team1, team2)