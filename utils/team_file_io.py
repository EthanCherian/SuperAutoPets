from objects.team import Team
from objects.pets import GET_PET
from utils.helpers import get_next_id

def import_team(name: str, id: int, turn: int) -> Team:
    team = Team(name)
    
    with open(f'data/team_{id}.csv', 'r') as f:
        for i, line in enumerate(f):
            if i == 0: continue         # skip header
            
            line = line.strip().split(',')

            if int(line[0]) < turn: continue
            if int(line[0]) > turn: break

            idx = int(line[1])
            pet = GET_PET(line[2])
            level = int(line[3])
            attack = int(line[4])
            health = int(line[5])
            perk = int(line[6])

            pet.set_level(level, scale_stats=True)
            attack = attack if attack > 0 else pet.attack
            health = health if health > 0 else pet.health
            pet.set_stats(attack, health)
            pet.receive_perk(perk)

            team.add_pet(pet, idx)
    
    if len(team.pets) == 0:
        raise Exception(f"No pets loaded from data/team_{id}.csv")

    return team

def export_team(team: Team, turn: int, id: int = -1):
    if id == -1: id = get_next_id()
    print(f"Exporting team {id} to data/team_{id}.csv")
    opt = 'w' if turn == 1 else 'a'
    with open(f'data/team_{id}.csv', opt) as f:
        if turn == 1:
            f.write("turn,index,name,level,attack,health,perk\n")
        for i, pet in enumerate(team.pets):
            if pet is None: continue

            f.write(f'{turn},{i},{pet.name},{pet.level()},{pet.battle_attack},{pet.battle_health},{pet.perk}\n')
    
    return id