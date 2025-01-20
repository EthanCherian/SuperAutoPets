import random
import os
from typing import List

from objects.animal import Animal
from objects.food import Food
from utils.constants import PERKS, PERK_EMOJIS, PERK_DESC, FOODS, FOOD_DESC
from utils.constants import PETS, PET_ABILITY_DESC
from utils.constants import ATTACK_EMOJI, HEALTH_EMOJI

flag = True

def debug(text):
    if flag:
        print(text)

def red(text):
    print(f'\033[91m    ** {text} **\033[0m')

def yellow(text):
    print(f'\033[93m    ** {text} **\033[0m')

def green(text):
    print(f'\033[92m    ** {text} **\033[0m')

def purple(text):
    print(f'\033[95m{text}\033[0m')

def blue(text):
    print(f'\033[94m{text}\033[0m')

def cyan(text):
    print(f'\033[96m{text}\033[0m')

def info(a: Animal, battle=False):
    temp = a.get_info(battle=battle)
    level = temp[2]
    perk = PERK_EMOJIS[PERKS[temp[3]]]
    attack = temp[4]
    health = temp[5]
    print(f'\033[96m {a} || level: {level} || {ATTACK_EMOJI}: {attack:2g} || {HEALTH_EMOJI}: {health:2g} || perk: {perk} \033[00m')

EXP_BAR = {
    0: "{__}",
    1: "{+_}",
    2: "{___}",
    3: "{+__}",
    4: "{++_}",
    5: "{+++}"
}

def shop_exp_display(a: Animal):
    level = a.level()
    exp = EXP_BAR[a.exp]
    if exp != "":
        return f"Lv.{level} {exp}"
    return f"Lv.{level}"

# ----------------------------------------

def get_random_id(exclude_id: int = None):
    # get a random valid team id, excluding the one passed in
    file_names = [file for file in os.listdir('data') if file.startswith('team_') and file.endswith('.csv')]
    selected_file = None
    while True:
        selected_file = random.choice(file_names)
        if selected_file != f'team_{exclude_id}.csv':
            break

    return int(selected_file.split('_')[1].split('.')[0])

def get_next_id():
    # get the next sequential team id to which a new team may be saved
    file_names = [file for file in os.listdir('data') if file.startswith('team_') and file.endswith('.csv')]
    file_ids = [int(file.split('_')[1].split('.')[0]) for file in file_names]

    if len(file_ids) == 0:
        return 1
    return max(file_ids) + 1

def get_random_pet_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
    # get count random pets from tiers
    ret = []
    pets_in_tier = [pet for pet in PETS if pet["tier"] in tiers and "token" not in pet]
    pet_names = [pet["name"] for pet in pets_in_tier]
    for _ in range(count):
        ret.append(random.choice(pet_names))
    
    # 1 in 10,000 of leftmost pet being sloth
    if random.randint(1, 10000) == 1:
        ret[0] = "sloth"
    
    return ret

def get_random_food_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
    # get count random foods from tiers
    ret = []
    foods_in_tier = [food for food in FOODS if food["tier"] in tiers and "token" not in food]
    food_names = [food["name"] for food in foods_in_tier]
    for _ in range(count):
        ret.append(random.choice(food_names))
    
    return ret

def get_pet_info(pet: Animal, specific: bool = False):
    # get info about pet, ie. tier, stats, and ability
    # if specific is True (request came from shop), get additional info about the arg pet instance
    pet_name = pet.name
    info = ""

    # get generic info
    info += f"{pet_name} || Icon: {str(pet)} || Tier {pet.tier} || {ATTACK_EMOJI}: {pet.attack} || {HEALTH_EMOJI}: {pet.health} || Perk: {PERK_EMOJIS[PERKS[pet.perk]]} : {PERK_DESC[PERKS[pet.perk]]}\n"
    info += f"\tAbility: {PET_ABILITY_DESC[pet_name]}\n"

    # get specific info
    if specific:
        exp_next_lvl = pet.exp_to_next_level()
        info += f"\tLevel: {pet.level()} || Exp To Next Level: {exp_next_lvl if exp_next_lvl > 0 else 'Max Level'}"
        temp_atk_buff = pet.battle_attack - pet.attack
        temp_health_buff = pet.battle_health - pet.health
        if temp_atk_buff != 0 or temp_health_buff != 0:
            info += f" || Temporary Buffs: {(temp_atk_buff, temp_health_buff)}"

    return info

def get_food_info(food: Food):
    # get info about food: effect, tier, perk/token status, etc.
    food_name = food.name
    info = ""

    info += f"{food_name} || Icon: {str(food)} || Tier {food.tier}"
    if not food.is_perk():
        info += f" || Boost: ({food.att_buff} {ATTACK_EMOJI}, {food.hp_buff} {HEALTH_EMOJI})\n"
    else:
        info += f" || Perk\n"
    
    info += f"\tEffect: {FOOD_DESC[food_name]}\n"
    
    return info

# these two were used for testing pets/foods

# def get_random_pet_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
#     ret = ["parrot", "sheep", "rooster", "mosquito"]
#     return ret

# def get_random_food_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
#     ret = ["canned food"]
#     return ret