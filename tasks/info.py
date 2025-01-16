from objects.pets import GET_PET
from objects.food import GET_FOOD
from utils.helpers import cyan, yellow, blue, get_food_info, get_pet_info
from utils.constants import PET_NAMES, FOOD_NAMES, PETS, FOODS, USE_EMOJI

class Info:
    ALL_PETS = None
    ALL_FOODS = None

    def __init__(self):
        if self.ALL_PETS is None:
            # self.ALL_PETS = [GET_PET(name) for name in PET_NAMES]
            self.ALL_PETS = { name : GET_PET(name) for name in PET_NAMES}
        if self.ALL_FOODS is None:
            # self.ALL_FOODS = [GET_FOOD(name) for name in FOOD_NAMES]
            self.ALL_FOODS = { name : GET_FOOD(name) for name in FOOD_NAMES}
    
    def show_all_pets(self):
        all_pets_by_tier = [[pet["name"] for pet in PETS if pet["tier"] == i and "token" not in pet] for i in range(1, 7)]
        token_pets = [pet["name"] for pet in PETS if "token" in pet]
        all_pets_by_tier.append(token_pets)

        # cyan(all_pets_by_tier)
        show = ""
        for i, pets_in_tier in enumerate(all_pets_by_tier):
            if i < 6:
                show += f"Tier {i+1}: "
            else:
                show += f"Token Pets: "

            for pet in pets_in_tier:
                show += f"{pet} {self.ALL_PETS[pet] if USE_EMOJI else ''} | "
            
            show += "\n"

        blue(show)
    
    def show_all_foods(self):
        all_foods_by_tier = [[food["name"] for food in FOODS if food["tier"] == i and "token" not in food] for i in range(1, 7)]
        token_foods = [food["name"] for food in FOODS if "token" in food]
        all_foods_by_tier.append(token_foods)

        # cyan(all_foods_by_tier)
        show = ""
        for i, foods_in_tier in enumerate(all_foods_by_tier):
            if i < 6:
                show += f"Tier {i+1}: "
            else:
                show += f"Token foods: "

            for food in foods_in_tier:
                show += f"{food} {self.ALL_FOODS[food] if USE_EMOJI else ''} | "
            
            show += "\n"

        blue(show)
    
    def display(self):
        while True:
            info_side = input("Would you like to get info on food or pets? (f/p, or \'quit\' to exit): ").lower()
            if info_side == "quit":
                break
            if info_side not in ["f", "p"]:
                yellow("Invalid input")
                continue

            if info_side == "f":
                self.show_all_foods()
            if info_side == "p":
                self.show_all_pets()

            expanded_side = "pet" if info_side == "p" else "food"
            prompt_name = input(f"Which {expanded_side} would you like to get info on? Enter the name: ").lower()

            if prompt_name in self.ALL_PETS:
                cyan(get_pet_info(self.ALL_PETS[prompt_name]))
            elif prompt_name in self.ALL_FOODS:
                cyan(get_food_info(self.ALL_FOODS[prompt_name]))
            else:
                yellow("Invalid input")
                continue

            input("Press \'Enter\' to continue...")
        
        blue("Exiting info mode...")