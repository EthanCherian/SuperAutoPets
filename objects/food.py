import copy

from utils.constants import FOODS, FOOD_NAMES, FOOD_EMOJIS
from utils.constants import PERKS, PERK_EMOJIS
from utils.constants import USE_EMOJI

class Food:
    name: str = ""
    tier: int = -1
    att_buff: int = -1
    hp_buff: int = -1
    perk: int = -1

    cost: int = -1
    temporary: bool = False
    count: int = -1
    shop: bool = False

    def __init__(self, name):
        self.name = name
        self.initialize_stats()

    def initialize_stats(self):
        loc = FOOD_NAMES.index(self.name)
        base_food = FOODS[loc]

        self.tier = base_food["tier"]
        self.att_buff = base_food["att_buff"]
        self.hp_buff = base_food["hp_buff"]

        if "perk" in base_food:
            self.perk = PERKS.index(self.name)
        
        self.cost = 3 if "cost" not in base_food else base_food["cost"]
        self.temporary = True if "temporary" in base_food else False
        self.count = 1 if "count" not in base_food else base_food["count"]

        if "shop" in base_food:
            self.shop = True

    def __str__(self):
        if USE_EMOJI:
            return f"{FOOD_EMOJIS[self.name]}"
        return f"{self.name}"

    def get_stats(self):
        return (self.att_buff, self.hp_buff)

    def is_perk(self):
        return self.perk > 0

# map from food name to food object
FOOD_MAP = {
    "apple": Food("apple"),
    "honey": Food("honey"),

    "sleeping pill": Food("sleeping pill"),
    "meat bone": Food("meat bone"),
    "cupcake": Food("cupcake"),

    "salad": Food("salad"),
    "garlic": Food("garlic"),

    "canned food": Food("canned food"),
    "pear": Food("pear"),

    "chili": Food("chili"),
    "chocolate": Food("chocolate"),
    "sushi": Food("sushi"),

    "steak": Food("steak"),
    "melon": Food("melon"),
    "mushroom": Food("mushroom"),
    "pizza": Food("pizza"),

    "bread crumbs": Food("bread crumbs"),
    "better apple": Food("better apple"),
    "best apple": Food("best apple"),
    "milk": Food("milk"),
    "better milk": Food("better milk"),
    "best milk": Food("best milk"),
}

# map from perk name to corresponding food object
PERK_MAP = {
    "honey": FOOD_MAP["honey"],
    "meat bone": FOOD_MAP["meat bone"],
    "garlic": FOOD_MAP["garlic"],
    "chili": FOOD_MAP["chili"],
    "melon": FOOD_MAP["melon"],
    "mushroom": FOOD_MAP["mushroom"],
    "steak": FOOD_MAP["steak"],
}

# functions to get clean copies of foods/perks from name
def GET_FOOD(name: str) -> Food:
    return copy.copy(FOOD_MAP[name])

def GET_PERK(name: str) -> Food:
    return copy.copy(PERK_MAP[name])