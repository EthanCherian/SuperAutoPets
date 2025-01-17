import math
from typing import List

from utils.helpers import get_random_pet_from_tiers, get_random_food_from_tiers
from utils.helpers import get_food_info, get_pet_info
from utils.helpers import debug, red, yellow, green, blue, purple, cyan, shop_exp_display
from utils.constants import GOLD_EMOJI, FREEZE_EMOJI, SPECIAL_EMOJI
from objects.pets import GET_PET
from objects.food import GET_FOOD, Food
from objects.animal import Animal
from objects.team import Team

class Shop:
    USER_OPTIONS = {
        "buy pet": 1,
        "sell pet": 2,
        "rearrange pet": 3,
        "buy food": 4,
        "freeze pet": 5,
        "freeze food": 6,
        "roll shop": 7,
        "team info": 8,
        "shop info": 9,
        "end turn": 0
    }

    TURN = -1
    HIGHEST_TIER_PET = 0
    NUM_ANIMAL_SLOTS = 0
    NUM_FOOD_SLOTS = 0
    SHOP_BUFFS = 0

    pets: List[Animal] = []
    foods: List[Food] = []

    frozen_pets: List[int] = []
    frozen_foods: List[int] = []

    team: Team = None
    gold: int = 10

    def __init__(self, turn: int, team: Team = None):
        self.TURN = turn
        self.initialize()
        self.team = team
    
    def __str__(self):
        ret = "\n-------------- SHOP --------------\n"
        ret += f"             Turn  {self.TURN}\n\n"

        ret += f"\nAnimals: (3 {GOLD_EMOJI} each)\n\n"
        for i, pet in enumerate(self.pets):
            pet_special = SPECIAL_EMOJI if pet.tier > self.HIGHEST_TIER_PET else ""
            ret += f"[{i+1}] :: {pet_special} {pet} @ {pet.get_battle_stats()} {pet_special}"
            if i in self.frozen_pets:
                ret += f" [{FREEZE_EMOJI}]"
            
            if i < len(self.pets) - 1:
                ret += " || "

        ret += f"\n\nFoods: (3 {GOLD_EMOJI} each, unless otherwise stated)\n\n"

        for i, food in enumerate(self.foods):
            ret += f"[{i+1}] :: {food}"
            if i in self.frozen_foods:
                ret += f" [{FREEZE_EMOJI}]"
            
            if food.cost != 3:
                ret += f" (costs {food.cost} {GOLD_EMOJI}!)"
            
            if i < len(self.foods) - 1:
                ret += " || "
        
        ret += "\n\n----------------------------------\n"

        return ret
    
    def initialize(self):
        old_highest_tier = self.HIGHEST_TIER_PET
        self.HIGHEST_TIER_PET = math.ceil(self.TURN / 2)
        self.HIGHEST_TIER_PET = min(self.HIGHEST_TIER_PET, 6)

        if old_highest_tier != self.HIGHEST_TIER_PET:
            green(f"Pets/foods up to tier {self.HIGHEST_TIER_PET} now available!")
        
        self.NUM_ANIMAL_SLOTS = 3 + math.floor((self.TURN - 1) / 4)
        self.NUM_ANIMAL_SLOTS = min(self.NUM_ANIMAL_SLOTS, 5)

        self.NUM_FOOD_SLOTS = 1 if self.TURN < 3 else 2

        if self.pets == []:
            self.pets = [None for _ in range(self.NUM_ANIMAL_SLOTS)]
        if self.foods == []:
            self.foods = [None for _ in range(self.NUM_FOOD_SLOTS)]

        self.set_animals()
        self.set_foods()
    
    def update(self, turn: int):
        self.TURN = turn
        self.initialize()

    def set_animals(self):
        # get rid of any excess pets beyond slot limits
        if len(self.pets) > self.NUM_ANIMAL_SLOTS:
            self.pets = self.pets[:self.NUM_ANIMAL_SLOTS]

        # move frozen pets to front
        counter = 0
        for i, fp in enumerate(self.frozen_pets):
            self.pets[counter] = self.pets[fp]
            self.frozen_pets[i] = counter
            counter += 1

        
        new_pets = get_random_pet_from_tiers(range(1, self.HIGHEST_TIER_PET + 1), self.NUM_ANIMAL_SLOTS)
        new_pets = [GET_PET(pet) for pet in new_pets]
        for pet in new_pets:
            # apply shop buffs from any previously purchased cans
            pet.receive_buff(self.SHOP_BUFFS, self.SHOP_BUFFS)

        num_frozen_pets = len(self.frozen_pets)
        # cut new pets to fit in unfrozen slots
        new_pets = new_pets[:self.NUM_ANIMAL_SLOTS - num_frozen_pets]
        for i, new_pet in enumerate(new_pets):
            if i + num_frozen_pets > len(self.pets) - 1:
                self.pets.insert(i + num_frozen_pets, new_pet)
            else:
                self.pets[i + num_frozen_pets] = new_pet

        return self.pets

    def set_foods(self):
        # get rid of any excess foods beyond slot limits
        if len(self.foods) > self.NUM_FOOD_SLOTS:
            self.foods = self.foods[:self.NUM_FOOD_SLOTS]
        
        # move frozen foods to front
        counter = 0
        for i, ff in enumerate(self.frozen_foods):
            self.foods[counter] = self.foods[ff]
            self.frozen_foods[i] = counter
            counter += 1

        new_foods = get_random_food_from_tiers(range(1, self.HIGHEST_TIER_PET + 1), self.NUM_FOOD_SLOTS)
        new_foods = [GET_FOOD(food) for food in new_foods]

        for i in range(len(new_foods)):
            if i not in self.frozen_foods:
                if i > len(self.foods) - 1:
                    self.foods.insert(i, new_foods[i])
                else:
                    self.foods[i] = new_foods[i]

        return self.foods

    def buy_shop_item(self, index, pets: bool = True):
        if pets:
            self.pets.pop(index)
            if index in self.frozen_pets:
                self.frozen_pets.remove(index)
        else:
            self.foods.pop(index)
            if index in self.frozen_foods:
                self.frozen_foods.remove(index)

    def freeze(self, index: int, pets: bool = True):
        if pets:
            if index not in self.frozen_pets: 
                self.frozen_pets.append(index)
            else:
                yellow(f"{index} already frozen")
        else:
            if index not in self.frozen_foods:
                self.frozen_foods.append(index)
            else:
                yellow(f"{index} already frozen")

    def unfreeze(self, index: int, pets: bool = True):
        if pets:
            if index in self.frozen_pets: 
                self.frozen_pets.remove(index)
            else:
                yellow(f"{index} not frozen")
        else:
            if index in self.frozen_foods:
                self.frozen_foods.remove(index)
            else:
                yellow(f"{index} not frozen")

    def roll(self):
        if self.gold >= 1:
            self.gold -= 1
        else:
            yellow("Not enough gold")
            return
        
        purple("Rolling shop...")

        self.set_animals()
        self.set_foods()

    def start_turn(self):
        trigger = self.team.on_start_turn()

        if not trigger:
            return
        
        if "gold" in trigger:            # swan
            gold_amt = trigger["gold"]
            debug(f"  gaining {gold_amt} {GOLD_EMOJI}")
            self.gold += gold_amt

        if "shop" in trigger:          # squirrel
            savings = trigger["shop"]
            debug(f"  saving {savings} {GOLD_EMOJI} on food")
            for food in self.foods:
                food.cost -= savings
                food.cost = max(food.cost, 0)

        if "stock" in trigger:         # worm
            trigger_food = trigger["stock"]
            food_stock = GET_FOOD(trigger_food)
            food_stock.cost = 2
            # debug(f"  stocking {food_stock.cost} {GOLD_EMOJI} {food_stock}")
            debug(f"  stocking {food_stock} at {food_stock.cost} {GOLD_EMOJI}")
            self.foods.append(food_stock)

    def end_turn(self):
        # verify that user is okay wasting excess gold
        if self.gold > 0:
            yellow(f"You have {self.gold} {GOLD_EMOJI} left, it will be discarded if you end turn.")
            gold_check = input("End turn anyway? (y/n) ").lower()
            if gold_check != "y" and gold_check != "yes":
                return False

        self.team.on_end_turn()
        return True

    def user_turn(self):
        self.gold = 10          # 10 gold per turn
        self.start_turn()

        while True:
            purple("\nYour team:\n")
            print(self.team.shop_display())

            purple("\nShop:")
            purple(f"You have {self.gold} {GOLD_EMOJI}.")
            print(self)

            purple("Options:\n")
            purple(f"   [{self.USER_OPTIONS['buy pet']}]  Buy pet")
            purple(f"   [{self.USER_OPTIONS['sell pet']}]  Sell pet")
            purple(f"   [{self.USER_OPTIONS['rearrange pet']}]  Rearrange pets\n")

            purple(f"   [{self.USER_OPTIONS['buy food']}]  Buy food\n")

            purple(f"   [{self.USER_OPTIONS['freeze pet']}]  Freeze/unfreeze pet")
            purple(f"   [{self.USER_OPTIONS['freeze food']}]  Freeze/unfreeze food\n")

            purple(f"   [{self.USER_OPTIONS['roll shop']}]  Roll shop\n")
            purple(f"   [{self.USER_OPTIONS['team info']}]  Info on your team")
            purple(f"   [{self.USER_OPTIONS['shop info']}]  Info on the shop\n")
            purple(f"   [{self.USER_OPTIONS['end turn']}]  End turn")

            user_input = input("\nWhat do you want to do? ")
            print()

            try:
                user_input = int(user_input)
                if user_input < 0 or user_input > 9:
                    raise ValueError
            except:
                yellow("Invalid input")

            if user_input == self.USER_OPTIONS["buy pet"]:
                self.buy_pet()
            
            if user_input == self.USER_OPTIONS["sell pet"]:
                self.sell_pet()
            
            if user_input == self.USER_OPTIONS["rearrange pet"]:
                self.rearrange_pet()

            if user_input == self.USER_OPTIONS["buy food"]:
                self.buy_food()
            
            if user_input == self.USER_OPTIONS["freeze pet"]:
                self.freeze_pet()
            
            if user_input == self.USER_OPTIONS["freeze food"]:
                self.freeze_food()

            if user_input == self.USER_OPTIONS["roll shop"]:
                self.roll()
            
            if user_input == self.USER_OPTIONS["team info"]:
                self.team_info()

            if user_input == self.USER_OPTIONS["shop info"]:
                self.shop_info()

            if user_input == self.USER_OPTIONS["end turn"]:
                purple("Ending turn...")

                end = self.end_turn()
                if end:
                    break
            
            input("Press \'Enter\' to continue...")

    def buy_pet(self):
        if self.gold < 3:
            yellow("Not enough gold")
            return

        if len(self.pets) < 1:
            yellow("Shop is empty")
            return

        shop_idx = input("Which pet do you want to buy? Enter the index: ")

        try:
            shop_idx = int(shop_idx)
            if shop_idx < 1 or shop_idx > len(self.pets):
                raise ValueError
        except:
            yellow("Invalid input")
            return

        pet = self.pets[shop_idx - 1]

        team_idx = input(f"Where do you want to place {pet} ? Enter the index: ")

        try:
            team_idx = int(team_idx)
            if team_idx < 1 or team_idx > 5:
                raise ValueError
        except:
            yellow("Invalid input")
            return

        combine = False
        if self.team.pets[team_idx - 1] is not None:
            occupied = self.team.pets[team_idx - 1]
            yellow(f"Slot {team_idx} is occupied by {occupied}")
            if occupied.name == pet.name:
                usr_comb = input("Do you want to combine them? (y/n) ").lower()
                combine = usr_comb == "y" or usr_comb == "yes"

        trigger = self.team.on_pet_buy(pet, team_idx - 1, combine)
        if "failed" in trigger:
            yellow(f"Purchase failed")
            return

        self.team.on_friend_buy(pet)
        self.buy_shop_item(shop_idx - 1, True)                 # remove from shop
        if shop_idx in self.frozen_pets:                # remove from frozen pets
            self.frozen_pets.remove(shop_idx)
        self.gold -= 3

        purple(f"You bought {pet} for 3 gold.")
        # handle remaining "on buy" abilities (ie. those interacting with shop)

        if "stock" in trigger:              # cow
            stock = trigger["stock"]
            food_stock = GET_FOOD(stock)
            debug(f"  stocking 2 free {food_stock}")
            self.foods = []
            self.frozen_foods = []
            for i in range(self.NUM_FOOD_SLOTS):
                self.foods.insert(i, food_stock)
                self.foods[i].cost = 0

        if "level up" in trigger:
            self.handle_level_up(trigger)

    def sell_pet(self):
        team_idx = input("Which pet do you want to sell? Enter the index: ")

        try:
            team_idx = int(team_idx)
            if team_idx < 1 or team_idx > 5:
                raise ValueError
        except:
            yellow("Invalid input")
            return

        pet = self.team.pets[team_idx - 1]

        if pet == None:
            yellow(f"No pet at index {team_idx}")
            return

        trigger = self.team.on_pet_sell(team_idx - 1)
        gold_returned = trigger["gold returned"]
        self.gold += gold_returned

        purple(f"You sold your {pet} for {gold_returned} {GOLD_EMOJI}.")
        # handle remaining "on sell abilities" (ie. those interacting with shop)

        if "effect" not in trigger:
            return

        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "buff":
            if target == "shop":            # duck
                attack_buff, health_buff = trigger["amount"]
                for shop_pet in self.pets:
                    debug(f"  {shop_pet} receiving {attack_buff, health_buff}")
                    shop_pet.receive_buff(attack_buff, health_buff)

        elif effect == "stock":
            if target == "food":            # pigeon
                stock_name = trigger["food"]
                amount = trigger["amount"]
                debug(f"  {pet} stocking {amount} {stock_name}(s)")

                for _ in range(amount):
                    self.foods.append(GET_FOOD(stock_name))

    def rearrange_pet(self):
        team_idx_1 = input("Which pet do you want to move? Enter the index: ")

        try:
            team_idx_1 = int(team_idx_1)
            if team_idx_1 < 1 or team_idx_1 > 5:
                raise ValueError
        except:
            yellow("Invalid input")
            return

        if self.team.pets[team_idx_1 - 1] is None:
            yellow(f"No pet at index {team_idx_1}")
            return

        team_idx_2 = input("Where should it go? Enter the index: ")

        try:
            team_idx_2 = int(team_idx_2)
            if team_idx_2 < 1 or team_idx_2 > 5:
                raise ValueError
        except:
            yellow("Invalid input")
            return

        if team_idx_1 == team_idx_2:
            yellow(f"Can't move pet to same index {team_idx_1}")
            return

        pet1 = self.team.pets[team_idx_1 - 1]

        if self.team.pets[team_idx_2 - 1] is None:
            yellow(f"Moving {pet1} to slot {team_idx_2}")
            self.team.pets[team_idx_2 - 1] = pet1
            self.team.pets[team_idx_1 - 1] = None
            return

        pet2 = self.team.pets[team_idx_2 - 1]

        combine = False
        if pet1.name == pet2.name:
            combine = input("Combine pets? (y/n) ").lower() == "y"

        if combine:
            # combine pets
            yellow(f"Combining {pet1} and {pet2}")
            trigger = self.team.combine_pets(team_idx_1 - 1, team_idx_2 - 1)
            self.handle_level_up(trigger)

        else:
            # swap pets
            yellow(f"Swapping {pet1} and {pet2}")
            self.team.switch_pets(team_idx_1 - 1, team_idx_2 - 1)

    def buy_food(self):
        if len(self.foods) < 1:
            yellow("Shop is empty")
            return

        shop_idx = input("Which food do you want to buy? Enter the index: ")

        try:
            shop_idx = int(shop_idx)
            if shop_idx < 1 or shop_idx > len(self.foods):
                raise ValueError
        except:
            yellow("Invalid input")
            return

        food = self.foods[shop_idx - 1]

        if self.gold < food.cost:
            yellow("Not enough gold")
            return

        self.gold -= food.cost
        self.buy_shop_item(shop_idx - 1, False)                # remove from shop
        if shop_idx in self.frozen_foods:               # remove from frozen foods
            self.frozen_foods.remove(shop_idx)

        if food.shop:             # canned food purchased
            # can is so different from other foods, need to handle separately
            trigger = self.team.on_shop_food_buy(food)
            purple(f"{food} purchased")

            pct_increase = trigger["increase"]
            base_effects = food.get_stats()
            boosted_effect = tuple(boost * (1 + pct_increase) for boost in base_effects)
            # apply buff to current shop pets
            for shop_pet in self.pets:
                shop_pet.receive_buff(*boosted_effect)

            # update shop buff to apply buff to all future shop pets
            self.SHOP_BUFFS += boosted_effect[0]

        elif food.count > 1:      # distributed food
            team_idcs = self.team.get_random_indices(food.count, False)

            purple(f"{food} distributed to {[str(self.team.pets[i]) for i in team_idcs]}")

            for team_idx in team_idcs:
                self.team.on_food_eat(team_idx, food)

        else:                   # targeted food
            team_idx = input(f"Which pet should eat {food} ? Enter the index: ")

            try:
                team_idx = int(team_idx)
                if team_idx < 1 or team_idx > 5:
                    raise ValueError
            except:
                yellow("Invalid input")
                return

            if self.team.pets[team_idx - 1] is None:
                yellow(f"No pet at index {team_idx - 1}")
                return

            trigger = self.team.on_food_eat(team_idx - 1, food)
            if not trigger:
                return

            # handle level up if necessary
            self.handle_level_up(trigger)

    def freeze_pet(self):
        frz_idx = input("Which pet do you want to freeze/unfreeze? Enter the index: ")

        try:
            frz_idx = int(frz_idx)
            if frz_idx < 1 or frz_idx > len(self.pets):
                raise ValueError
        except:
            yellow("Invalid input")
            return

        if frz_idx - 1 in self.frozen_pets:
            self.frozen_pets.remove(frz_idx - 1)
            purple(f"You unfroze {self.pets[frz_idx - 1]}")
        else:
            self.frozen_pets.append(frz_idx - 1)
            purple(f"You froze {self.pets[frz_idx - 1]}")

    def freeze_food(self):
        frz_idx = input("Which food do you want to freeze/unfreeze? Enter the index: ")

        try:
            frz_idx = int(frz_idx)
            if frz_idx < 1 or frz_idx > len(self.foods):
                raise ValueError
        except:
            yellow("Invalid input")
            return

        if frz_idx - 1 in self.frozen_foods:
            self.frozen_foods.remove(frz_idx - 1)
            purple(f"You unfroze {self.foods[frz_idx - 1]}")
        else:
            self.frozen_foods.append(frz_idx - 1)
            purple(f"You froze {self.foods[frz_idx - 1]}")

    def handle_level_up(self, trigger):
        # if pet levels up, add new pet to shop from next highest tier
        if trigger is None or "level up" not in trigger:
            return

        purple(f"A pet levelled up, generating new pet of higher tier!")

        higher_tier = self.HIGHEST_TIER_PET + 1
        higher_tier = min(higher_tier, 6)           # cap at 6
        new_pet_name = get_random_pet_from_tiers([higher_tier], 1)[0]
        new_pet = GET_PET(new_pet_name)

        self.pets.append(new_pet)

    def team_info(self):
        # get index of pet to get info on
        if len(self.team.pets) < 1:
            yellow("No pets in team")
            return
        
        pet_idx = input("Which pet do you want to get info on? Enter the index (1-5), or 0 for entire team: ")
        try:
            pet_idx = int(pet_idx)
            if pet_idx < 0 or pet_idx > 5:
                raise ValueError
        except:
            yellow("Invalid input")
            return
        
        # get relevant info
        info = ""
        if pet_idx == 0:
            # for entire team
            for pet in self.team.pets:
                if pet is None:
                    continue
                info += get_pet_info(pet, specific=True) + "\n"
        else:
            # for single pet
            info = get_pet_info(self.team.pets[pet_idx - 1], specific=True)
        
        cyan(info)

    def shop_info(self):
        # determine which side of shop to get info on
        shop_side = input("Would you like to get info on food or pets? (f/p): ").lower()
        if shop_side not in ["f", "p"]:
            yellow("Invalid input")
            return
        
        info = ""
        if shop_side == "f":
            if len(self.foods ) < 1:
                yellow("No pets in shop")
                return
            # get info on food
            food_idx = input("Which food do you want to get info on? Enter the index, or 0 for entire stock: ")
            try:
                food_idx = int(food_idx)
                if food_idx < 0 or food_idx > len(self.foods):
                    raise ValueError
            except:
                yellow("Invalid input")
                return
            
            if food_idx == 0:
                # for entire stock
                for food in self.foods:
                    info += get_food_info(food) + "\n"
            else:
                # for single food
                info = get_food_info(self.foods[food_idx - 1])
        
        elif shop_side == "p":
            if len(self.pets) < 1:
                yellow("No pets in shop")
                return
            # get info on pets
            pet_idx = input("Which pet do you want to get info on? Enter the index, or 0 for entire stock: ")
            try:
                pet_idx = int(pet_idx)
                if pet_idx < 0 or pet_idx > len(self.pets):
                    raise ValueError
            except:
                yellow("Invalid input")
                return
            
            if pet_idx == 0:
                # for entire stock
                for pet in self.pets:
                    if pet is None:
                        continue
                    info += get_pet_info(pet) + "\n"
            else:
                # for single pet
                info = get_pet_info(self.pets[pet_idx - 1])

        cyan(info)