import random
import os
from typing import List

from objects.animal import Animal
from utils.constants import PERKS, PERK_EMOJIS, FOODS
from utils.constants import PETS

flag = True

def debug(text):
    if flag:
        print(text)

def error(text):
    if flag:
        print(f'\033[91m    ** {text} **\033[0m')

def warning(text):
    if flag:
        print(f'\033[93m    ** {text} **\033[0m')

def success(text):
    if flag:
        print(f'\033[92m    ** {text} **\033[0m')

def show(text):
    if flag:
        print(f'\033[95m{text}\033[0m')

def prompt(text):
    if flag:
        print(f'\033[94m {text} \033[0m')

def info(a: Animal, battle=False):
    temp = a.get_info(battle=battle)
    level = temp[2]
    perk = PERK_EMOJIS[PERKS[temp[3]]]
    attack = temp[4]
    health = temp[5]
    print(f'\033[96m {a} || level: {level} || 👊: {attack:2g} || 💖: {health:2g} || perk: {perk} \033[00m')

EXP_BAR = {
    0: "",
    1: "½",
    2: "",
    3: "⅓",
    4: "⅔",
    5: ""
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
    
    return ret

def get_random_food_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
    # get count random foods from tiers
    ret = []
    foods_in_tier = [food for food in FOODS if food["tier"] in tiers and "token" not in food]
    food_names = [food["name"] for food in foods_in_tier]
    for _ in range(count):
        ret.append(random.choice(food_names))
    
    return ret

# these two were used for testing pets/foods

# def get_random_pet_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
#     ret = ["sheep", "sheep", "sheep"]
#     return ret

# def get_random_food_from_tiers(tiers: List[int], count: int = 1) -> List[str]:
#     ret = ["canned food"]
#     return ret