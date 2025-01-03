from __future__ import annotations
from typing import List
import random
import copy

from objects.animal import Animal
from objects import pets as PETS
from objects.food import Food, PERK_EMOJIS, PERKS, GET_FOOD
from utils.helpers import debug, error, warning, success, info, shop_exp_display

class Team:
    name: str = ""
    num_wins: int = 0
    num_lives: int = 5

    pets: List[Animal] = []
    battle_pets: List[Animal] = []

    lost_last_battle: bool = False

    def __init__(self, name):
        self.name = name
        self.pets = [None, None, None, None, None]

    def __str__(self):
        return '  '.join([str(pet) for pet in self.pets if pet])

    def battle_won(self):
        self.num_wins += 1
        self.lost_last_battle = False

    def battle_lost(self):
        self.num_lives -= 1
        self.lost_last_battle = True

    def print(self):
        [success(f"{pet}  @ {pet.get_battle_stats()}") for pet in self.battle_pets]

    def shop_display(self):
        ret = "FRONT --> "
        
        for i in range(5):
            if i < len(self.pets) and self.pets[i]:
                pet = self.pets[i]
                ret += f"[{i+1}] :: {pet} @ {pet.get_battle_stats()} @ {shop_exp_display(pet)}"

                if i < 4:
                    ret += " || "
            
            else:
                ret += f"[{i+1}] :: Empty"
                if i < 4:
                    ret += " || "
        
        ret += " <-- BACK"
        return ret

    def full_info(self):
        [info(pet) for pet in self.pets if pet]

    def battle_info(self):
        [info(pet, True) for pet in self.battle_pets if pet]

    def length(self, battle: bool = False) -> int:
        pets = self.battle_pets if battle else self.pets
        return sum(pet is not None for pet in pets)

    def get_random_indices(self, n: int, in_battle: bool = False, exclude: int = -1) -> List[int]:
        # get n random indices, excluding arg value
        # only choose indices that are not None in the appropriate pets list
        pets = self.battle_pets if in_battle else self.pets
        full_indices = [pets.index(pet) for pet in pets if pet is not None]
        indices = set()             # want distinct indices

        upper_idx = self.length(in_battle)
        while len(indices) < min(n, upper_idx):
            temp = random.randint(0, upper_idx - 1)
            if temp != exclude and temp in full_indices:
                indices.add(temp)

        return list(indices)

    def add_pet(self, pet: Animal, index: int, in_battle: bool = False, combine: bool = False):
        pets = self.battle_pets if in_battle else self.pets

        if in_battle:
            # summoning mid-battle
            if len(pets) == 0 or sum(pet is not None for pet in pets) < 5:
                pets.insert(index, pet)
                self.on_friend_summon(pet, in_battle)
                return True

            else:
                return False

        # in shop
        if pets[index] is None:
            # inserting into empty space
            pets[index] = pet
            self.on_friend_summon(pet, in_battle)
            return True

        if combine:
            # collision (matching) --> combine
            pets[index].combine(pet)
            return True
        
        elif any(pet is None for pet in pets):
            # collision (non-matching) --> shift pets and insert
            empty_indices_right = [i for i in range(index, len(pets)) if pets[i] is None]
            if len(empty_indices_right) == 0:
                # attempting to insert to the right of empty space(s)
                return False
            
            pets.pop(empty_indices_right[0])        # remove empty space
            pets.insert(index, pet)                 # insert pet, shifting others rightto fill empty space
            self.on_friend_summon(pet, in_battle)
            return True

        return False

    def switch_pets(self, index1: int, index2: int):
        self.pets[index1], self.pets[index2] = self.pets[index2], self.pets[index1]

    def combine_pets(self, index1: int, index2: int):
        pet1 = self.pets[index1]
        pet2 = self.pets[index2]
        l = pet2.level()
        pet2.combine(pet1)

        self.pets[index2] = pet2
        self.pets[index1] = None
        if pet2.level() > l:
            self.on_pet_level_up(index2)
            return {
                "level up": True
            }

    def reset(self):
        for pet in self.pets:
            if pet:
                pet.reset()

        self.battle_pets = []

    def battle_turn(self, opposing_team: Team):
        # front-most pet of each team attack each other
        pet = self.battle_pets[0]
        opposing_pet = opposing_team.battle_pets[0]
        
        # before attack
        self.before_attack()
        opposing_team.before_attack()

        self_splash, opp_splash = False, False
        # attack (hurt, friend ahead attack)
        if opposing_pet.battle_perk == 5 and len(self.battle_pets) > 1:        # opposing pet has chili
            debug(f"  {opposing_pet} splashing 5 damage to {self.battle_pets[1]}")
            self_splash = self.on_hurt(1, 5, opposing_team, True)
        self_hit = self.on_hurt(0, opposing_pet.battle_attack, opposing_team, True, opposing_pet)

        if pet.battle_perk == 5 and len(opposing_team.battle_pets) > 1:        # friendly pet has chili
            debug(f"  {pet} splashing 5 damage to {opposing_team.battle_pets[1]}")
            opp_splash = opposing_team.on_hurt(1, 5, self, True)
        opp_hit = opposing_team.on_hurt(0, pet.battle_attack, self, True, pet)

        # check knockout (direct attack or splash damage)
        if (self_splash or self_hit) and (not opp_hit):
            # debug(f"  {opposing_pet} KO'ed {pet}")
            opposing_team.on_knockout(pet, self)
        if (opp_splash or opp_hit) and (not self_hit):
            # debug(f"  {pet} KO'ed {opposing_pet}")
            self.on_knockout(opposing_pet, opposing_team)

        self.friend_ahead_attacks(opposing_team, pet)
        opposing_team.friend_ahead_attacks(self, opposing_pet)

        # after attack
        self.after_attack(opposing_team)
        opposing_team.after_attack(self)

    def before_attack(self):
        if len(self.battle_pets) < 1:
            return
        # only boar
        pet = self.battle_pets[0]
        trigger = pet.before_attack()
        if trigger is None:
            return
        
        if trigger["effect"] == "buff":
            attack_buff, health_buff = trigger["amount"]
            pet.receive_buff(attack_buff, health_buff, temporary=True)

    def friend_ahead_attacks(self, opposing_team: Team, friend_ahead: Animal):
        if len(self.battle_pets) == 0:
            return
        
        idx_behind = 0 if friend_ahead != self.battle_pets[0] else 1

        if idx_behind >= len(self.battle_pets):
            return
        
        friend_behind = self.battle_pets[idx_behind]
        if not friend_behind:
            return

        trigger = friend_behind.on_friend_ahead_attack()
        if trigger is None:
            return

        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "damage":
            if target == "random":              # snake
                damage = trigger["amount"]
                random_index = opposing_team.get_random_indices(1, True)
                if len(random_index) < 1:
                    return
                random_index = random_index[0]
                debug(f"  {friend_behind} damaging {opposing_team.battle_pets[random_index]} for {damage} damage")
                opposing_team.on_hurt(random_index, damage, self)
        
        if effect == "buff":                    # kangaroo
            if target == "self":
                attack_buff, health_buff = trigger["amount"]
                debug(f"  {friend_behind} buffing self w/ {(attack_buff, health_buff)}")
                friend_behind.receive_buff(attack_buff, health_buff, temporary=True)

    def after_attack(self, opposing_team: Team):
        if len(self.battle_pets) < 1:
            return

        # just elephant
        trigger = self.battle_pets[0].after_attack()

        if trigger is None:
            return
        
        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "damage":
            if target == "behind":
                damage = trigger["damage"]

                for index in range(1, trigger["count"] + 1):
                    if index >= len(self.battle_pets):
                        break

                    debug(f"  {self.battle_pets[0]} damaging {self.battle_pets[index]} for {damage} damage")
                    self.on_hurt(index, damage, opposing_team)

    def on_battle_start(self, opposing_team: Team):
        # prepare pets for battle + trigger "start of battle" abilities

        if len(self.battle_pets) != 0:        # team already prepared
            return
        for pet in self.pets:
            if not pet:
                continue
            pet.prepare_battle()

        # create copy of pets to be used in battle
        self.battle_pets = copy.copy(self.pets)
        self.battle_pets = [pet for pet in self.battle_pets if pet]

        # copy of battle pets for "start of battle" abilities
        starting_pets = copy.copy(self.battle_pets)

        for idx, pet in enumerate(starting_pets):
            if not pet:
                continue

            if pet.name == "parrot":        # fail-safe to get parrot's copy set up appropriately
                if pet.copy_pet is None:
                    if idx == 0:      # parrot is at front, no one to copy
                        continue

                    copy_pet = self.battle_pets[idx - 1]
                    debug(f"  {pet} copying {copy_pet}")
                    pet.copy_pet = copy_pet

            trigger = pet.on_battle_start()

            if trigger is None: 
                continue

            effect = trigger["effect"]
            target = trigger["target"]

            if effect == "damage":
                # set up opposing team if needed
                if len(opposing_team.battle_pets) == 0:
                    opposing_team.on_battle_start(self)

                count = trigger["count"]
                damage = trigger["damage"]
                if target == "random":                  # mosquito, leopard
                    random_indices = opposing_team.get_random_indices(count, True)
                    
                    for index in random_indices:
                        debug(f"  {pet} damaging {opposing_team.battle_pets[index]} for {damage} damage")
                        opposing_team.on_hurt(index, damage, opposing_team=self, in_battle=True)
                
                if target == "lowest":
                    for _ in range(count):              # dolphin
                        lowest_health_index = min(range(len(opposing_team.battle_pets)), key=lambda i: opposing_team.battle_pets[i].battle_health)
                        debug(f"  {pet} damaging {opposing_team.battle_pets[lowest_health_index]} for {damage} damage")
                        opposing_team.on_hurt(lowest_health_index, damage, opposing_team=self, in_battle=True)
                
                if target == "last":                    # crocodile
                    last_idx = len(opposing_team.battle_pets) - 1

                    for _ in range(count):
                        debug(f"  {pet} damaging {opposing_team.battle_pets[last_idx]} for {damage} damage")
                        if opposing_team.on_hurt(last_idx, damage, opposing_team=self, in_battle=True):
                            last_idx -= 1

            elif effect == "copy":
                if target == "health":                  # crab
                    highest_health_index = max(range(len(self.battle_pets)), key=lambda i: self.battle_pets[i].battle_health)
                    highest_health_pet = self.battle_pets[highest_health_index]
                    pet.battle_health = int(trigger["amount"] * highest_health_pet.battle_health)
                    debug(f"  {pet} copying {highest_health_pet} for {trigger['amount']} * {highest_health_pet.battle_health} health")

            elif effect == "buff":
                if target == "attack":          # dodo
                    idx_ahead = idx - 1
                    if idx_ahead < 0:
                        return
                    
                    pet_ahead = self.battle_pets[idx_ahead]
                    pet_ahead.battle_attack += int(trigger["amount"] * pet.battle_attack)
                    debug(f"  {pet} buffing {pet_ahead} for {trigger['amount']} * {pet.battle_attack} attack --> {pet_ahead.get_battle_stats()}")
                
                if target == "all":             # armadillo
                    health_buff = trigger["amount"][1]

                    for other_pet in self.battle_pets:
                        other_pet.battle_health += health_buff
                        debug(f"  {pet} buffing {other_pet} for {health_buff} health --> {other_pet.get_battle_stats()}")
                    
                    if len(opposing_team.battle_pets) == 0:
                        opposing_team.on_battle_start(self)
                    for other_pet in opposing_team.battle_pets:
                        other_pet.battle_health += health_buff
                        debug(f"  {pet} buffing {other_pet} for {health_buff} health --> {other_pet.get_battle_stats()}")

            elif effect == "debuff":
                if target == "health":          # skunk
                    amount = trigger["amount"]
                    highest_health_index = max(range(len(opposing_team.battle_pets)), key=lambda i: opposing_team.battle_pets[i].battle_health)
                    highest_health_pet = opposing_team.battle_pets[highest_health_index]

                    debug(f"  {pet} removing {int(amount*100):2d}% health from {highest_health_pet} @ {highest_health_pet.get_battle_stats()}")
                    highest_health_pet.battle_health *= (1 - amount)
                    highest_health_pet.battle_health = max(1, int(highest_health_pet.battle_health))

            elif effect == "faint":
                if target == "ahead":           # whale
                    idx_ahead = idx - 1
                    if idx_ahead < 0:
                        continue
                    debug(f"  {pet} fainting {self.battle_pets[idx_ahead]}")
                    pet.summon_pet = PETS.GET_PET(self.battle_pets[idx_ahead].name)
                    self.on_pet_faint(idx_ahead, opposing_team, in_battle=True)

    def on_pet_faint(self, index: int, opposing_team: Team, in_battle: bool = True):
        # handle "on faint" abilities

        pets = self.battle_pets if in_battle else self.pets
        fainted_pet = pets[index]
        debug(f"  {fainted_pet} fainted")
        trigger = fainted_pet.on_faint()        # call Animal on_faint() to check for relevant faint perks
        if in_battle:
            pets.pop(index)
        else:
            pets[index] = None

        # check friend behind's ability (ox)
        if self.length(in_battle) != 0:
            temp_trigger = pets[0].on_friend_ahead_faints()

            if temp_trigger and temp_trigger["effect"] == "buff":       # ox
                amt = temp_trigger["amount"][0]
                perk = temp_trigger["perk"]

                debug(f"  {pets[0]} gaining {amt} attack and {PERK_EMOJIS[PERKS[perk]]}")
                pets[0].receive_buff(amt, 0, temporary=in_battle)
                pets[0].receive_perk(perk, temporary=in_battle)

        # check for friend_faint triggers
        temp_pets = copy.copy(pets)
        for pet in temp_pets:
            if not pet:
                continue
            temp_trigger = pet.on_friend_faint()

            if not temp_trigger:
                continue

            effect = temp_trigger["effect"]
            target = temp_trigger["target"]

            if effect == "summon":          # fly
                if target == "team":
                    if fainted_pet.name == "zombie fly":
                        # ignore fly summon if fainted pet is zombie fly
                        continue

                    token = temp_trigger["token"]
                    try:
                        pet.summon_msg(token)
                    except:
                        pass
                    count = temp_trigger["count"]
                    for _ in range(count):
                        c = copy.copy(token)
                        c.prepare_battle()
                        self.add_pet(c, index, in_battle)

            elif effect == "buff":          # shark
                if target == "self":
                    attack_buff, health_buff = temp_trigger["amount"]
                    pet.receive_buff(attack_buff, health_buff, temporary=in_battle)
                    debug(f"  {pet} buffing self w/ {(attack_buff, health_buff)} --> {pet.get_battle_stats()}")

        if trigger is None or trigger == {}:
            return

        effect = trigger["effect"] if "effect" in trigger else "none"
        target = trigger["target"] if "target" in trigger else "none"


        if effect == "summon":
            token = trigger["token"]          # pet to be summoned
            count = trigger["count"]

            if target == "team":        # summoning friend (eg. sheep, rooster, whale, etc.)
                for _ in range(count):
                    c = copy.copy(token)
                    c.prepare_battle()
                    self.add_pet(c, index, in_battle)

            elif target == "enemy":     # summoning enemy (eg. rat)
                for _ in range(count):
                    c = copy.copy(token)
                    c.prepare_battle()
                    opposing_team.add_pet(c, 0, True)
        
        elif effect == "buff":              # buffing friend
            attack_buff, health_buff = trigger["amount"]

            if target == "random":          # ant
                random_idx = self.get_random_indices(1, in_battle)[0]
                random_pet = pets[random_idx]
                debug(f"  buffing random pet: {random_pet} w/ {(attack_buff, health_buff)}")
                random_pet.receive_buff(attack_buff, health_buff, temporary=in_battle)
            
            elif target == "2":             # flamingo
                indices_buff = [index, index + 1]
                indices_buff = [i for i in indices_buff if i <= 4]      # keep buff within team bounds

                for i in indices_buff:
                    try:
                        debug(f"   buffing pet: {pets[i]} w/ {(attack_buff, health_buff)}")
                        pets[i].receive_buff(attack_buff, health_buff, temporary=in_battle)
                    except:
                        pass
            
            elif target == "friends":       # mammoth
                for pet in pets:
                    if not pet:
                        continue
                    debug(f"  {fainted_pet} buffing {pet} w/ {(attack_buff, health_buff)}")
                    pet.receive_buff(attack_buff, health_buff, temporary=in_battle)

        elif effect == "perk":
            if target == "behind":          # turtle
                perk = trigger["perk"]
                count = trigger["count"]

                indices_buff = range(index, index + count)
                indices_buff = [i for i in indices_buff if i < len(pets)]

                for idx in indices_buff:
                    debug(f"  giving {pets[idx]} {PERK_EMOJIS[PERKS[perk]]}")
                    pets[idx].receive_perk(perk, temporary=in_battle)

        elif effect == "damage":
            if target == "adjacent":        # badger
                if index != 0 or not in_battle:     # damaging friends only
                    behind = index      # pets.pop() shifted animals forward
                    ahead = index - 1

                    if behind < len(pets):
                        debug(f"  damaging {pets[behind]} for {trigger['damage']} damage")
                        self.on_hurt(behind, trigger["damage"], opposing_team, in_battle)
                    if ahead >= 0:
                        debug(f"  damaging {pets[ahead]} for {trigger['damage']} damage")
                        self.on_hurt(ahead, trigger["damage"], opposing_team, in_battle)

                else:                               # front of team, damaging 1 enemy
                    behind = index      # pets.pop() shifted animals forward
                    ahead = 0           # enemy team

                    if behind < len(pets):
                        debug(f"  damaging {pets[behind]} for {trigger['damage']} damage")
                        self.on_hurt(behind, trigger["damage"], opposing_team, in_battle)
                    if len(opposing_team.battle_pets) > 0:
                        debug(f"  damaging {opposing_team.battle_pets[ahead]} for {trigger['damage']} damage")
                        opposing_team.on_hurt(ahead, trigger["damage"], self, in_battle)

            elif target == "all":               # hedgehog
                debug(f"  damaging all pets for {trigger['amount']} damage")
                pets_range = list(range(len(pets)))
                for i in pets_range:
                    fainted = self.on_hurt(i, trigger["amount"], opposing_team, in_battle)
                    if fainted:
                        pets_range.pop()

                if in_battle:
                    opposing_pets_range = list(range(len(opposing_team.battle_pets)))
                    for i in opposing_pets_range:
                        fainted = opposing_team.on_hurt(i, trigger["amount"], self, in_battle)
                        if fainted:
                            opposing_pets_range.pop()

        if "honey" in trigger:          # fainted pet had honey --> summon bee @ (1, 1)
            bee = Animal("bee")
            debug(f"  summoning {bee} @ {bee.get_battle_stats()}")
            self.add_pet(bee, index, in_battle)

        if "mushroom" in trigger:       # fainted pet had mushroom --> summon clone of pet @ (1, 1)
            clone = PETS.GET_PET(fainted_pet.name)
            clone.set_level(fainted_pet.level())        # clone has same level as original pet
            clone.set_stats(1, 1)
            clone.prepare_battle()
            debug(f"  summoning cloned {clone} @ {clone.get_battle_stats()}")
            self.add_pet(clone, index, in_battle)

    def on_friend_summon(self, friend: Animal, in_battle: bool = False):
        # handle "friend summoned" abilities

        pets = self.battle_pets if in_battle else self.pets
        for pet in pets:
            if pet and pet is not friend:
                trigger = pet.on_friend_summon()
                if not trigger:
                    continue

                effect = trigger["effect"]
                target = trigger["target"]

                if effect == "buff":
                    attack_buff, health_buff = trigger["amount"]
                    if target == "friend":      # turkey + horse
                        temporary = True if "temporary" in trigger else in_battle

                        friend.receive_buff(attack_buff, health_buff, temporary=temporary)
                        debug(f"  {pet} buffing {friend} for {attack_buff, health_buff} --> {friend.get_battle_stats()}")
                    
                    if target == "self":        # dog
                        pet.receive_buff(attack_buff, health_buff, temporary=True)


    def on_hurt(self, index: int, damage: int, opposing_team: Team, in_battle: bool = True, attacker: Animal = None):
        # handle "hurt" abilities

        pet_fainted = False         # useful to know whether pet fainted as a result of incoming damage
        
        pets = self.battle_pets if in_battle else self.pets
        pet = pets[index]
        trigger = pet.on_hurt(damage, attacker)
        if pet.battle_health <= 0:
            self.on_pet_faint(index, opposing_team, in_battle)
            pet_fainted = True
        if not trigger:
            return pet_fainted
        
        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "damage":              # blowfish
            if target == "random" and in_battle:
                random_idx = opposing_team.get_random_indices(1, in_battle)[0]
                debug(f"  {pet} dealing {trigger['damage']} damage to {opposing_team.battle_pets[random_idx]}")
                opposing_team.on_hurt(random_idx, trigger["damage"], opposing_team=self, in_battle=True)

        elif effect == "buff":
            attack_buff, health_buff = trigger["amount"]
            if target == "self":            # peacock
                debug(f"  {pet} gaining {attack_buff} attack")
                pet.receive_buff(attack_buff, health_buff, temporary=in_battle)

            elif target == "behind":        # camel
                behind_idx = (index + 1) if pet.battle_health > 0 else index
                if behind_idx >= len(pets):
                    return pet_fainted
                pet_behind = pets[behind_idx]
                debug(f"  {pet} giving {attack_buff, health_buff} to {pet_behind}")
                pet_behind.receive_buff(attack_buff, health_buff, temporary=in_battle)

        elif effect == "perk":              # gorilla
            perk = int(trigger["perk"])
            pet.receive_perk(perk, temporary=in_battle)

        return pet_fainted

    def on_food_eat(self, index: int, food: Food):
        # handle food eating mechanics and "self/friend eats food" abilities

        food_friend = self.pets[index]
        base_food = GET_FOOD(food.name)     # create copy of food to be safe
        food_effects = food.get_stats()

        # check for friendly food eaten effects
        for pet in self.pets:
            if not pet:
                continue
            trigger = pet.on_friend_eats_food()

            if not trigger:
                continue

            effect = trigger["effect"]
            target = trigger["target"]

            if effect == "buff":              # rabbit
                attack_buff, health_buff = trigger["amount"]
                if target == "ate":
                    debug(f"  {food_friend} getting {attack_buff, health_buff} from {pet}")
                    food_friend.receive_buff(attack_buff, health_buff)
            
            if effect == "increase":           # cat
                if target == "ate" and not food.is_perk():
                    amount = trigger["amount"]
                    increase = tuple(i * amount for i in base_food.get_stats())
                    food_effects = tuple(i + j for i, j in zip(food_effects, increase))
                    debug(f"  {pet} increasing effects of {food} by {amount*100}%, now giving {food_effects}")

        if food.is_perk():          # give appropriate perk
            if food.name != "sleeping pill" and food.name != "chocolate":           # these two work differently
                food_friend.receive_perk(food.perk, temporary=food.temporary)
        else:                       # pass buff
            food_friend.receive_buff(*food_effects, temporary=food.temporary)

        res = {}
        if food.name == "chocolate":
            l = food_friend.level()
            food_friend.gain_exp(1)

            if l < food_friend.level():             # check if pet leveled up, inform shop if so
                self.on_pet_level_up(index)
                res = {
                    "level up": True
                }

        elif food.name == "sleeping pill":
            self.on_pet_faint(index, None, False)

        trigger = food_friend.on_food_eaten()

        if not trigger:
            return res

        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "buff":              # seal
            if target == "3":
                amount = trigger["amount"]
                random_indices = self.get_random_indices(3, in_battle=False, exclude=index)
                
                for idx in random_indices:
                    debug(f"  {food_friend} giving {amount} attack to {self.pets[idx]}")
                    self.pets[idx].receive_buff(amount, 0, False)
        
        return res

    def on_shop_food_buy(self, food: Food):
        # just for purchases of canned food
        food_inc = { "increase": 0 }
        for pet in self.pets:
            if not pet:
                continue

            trigger = pet.on_friend_eats_food()
            if not trigger:
                continue

            effect = trigger["effect"]
            target = trigger["target"]

            if effect != "increase" or target != "ate":
                continue

            amount = trigger["amount"]
            inc = food_inc["increase"]
            food_inc.update({ "increase": inc + amount })
        
        return food_inc

    def on_knockout(self, victim: Animal, opposing_team: Team):
        # handle "on knockout" abilities

        pet = self.battle_pets[0]

        trigger = pet.on_knockout()
        if not trigger:
            return

        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "buff":                    # hippo
            if target == "self":
                attack_buff, health_buff = trigger["amount"]
                if victim.tier >= 4:
                    attack_buff *= 2
                    health_buff *= 2

                debug(f"  {pet} KO'ed {victim}, gaining {attack_buff, health_buff}")
                pet.receive_buff(attack_buff, health_buff, temporary=True)
        
        elif effect == "damage":                # rhino
            if target == "next":
                damage = trigger["damage"]
                if victim.tier == 1:
                    damage *= 2

                debug(f"  {pet} KO'ed {victim}, dealing {damage} damage to {opposing_team.battle_pets[0]}")
                got_ko = opposing_team.on_hurt(0, damage, opposing_team=self, in_battle=True)

                if got_ko and len(opposing_team.battle_pets) != 0:         # check for chaining knockouts
                    self.on_knockout(opposing_team.battle_pets[0], opposing_team)

    def on_pet_buy(self, friend: Animal, index: int, combine: bool = False):
        # handle "on buy" abilities

        existing_pet = None
        ret = {}
        level = 100
        if self.pets[index] is not None:            # check if combining with existing pets
            existing_pet = self.pets[index]
            level = existing_pet.level()

        pet_added = self.add_pet(friend, index, in_battle=False, combine=combine)
        if not pet_added:
            return { "failed": True }

        trigger = None
        if combine:
            trigger = self.pets[index].on_buy()
        else:
            trigger = friend.on_buy()

        if existing_pet is not None and level < existing_pet.level():
            # if leveled up, inform shop
            debug(f"  {existing_pet} levelled up!")
            self.on_pet_level_up(index)
            ret.update({ "level up": True })

        if not trigger:
            return ret
        
        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "buff":            # otter
            if target == "random":
                attack_buff, health_buff = trigger["amount"]
                count = trigger["count"]
                random_idx = self.get_random_indices(count, False, index)
                for i in random_idx:
                    debug(f"  {friend} giving {attack_buff, health_buff} to {self.pets[i]}")
                    self.pets[i].receive_buff(attack_buff, health_buff)
            
        elif effect == "stock":          # cow
            ret.update({"stock": trigger["stock"]})
        
        return ret

    def on_pet_sell(self, index: int):
        # handle "on sell" abilities

        pet = self.pets[index]
        self.pets[index] = None
        trigger = pet.on_sell()

        if not trigger:
            return {
                "gold returned": pet.level()
            }
        
        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "gold":            # pig
            if target == "shop":
                amount = trigger["amount"]
                return {
                    "gold returned": pet.level() + amount
                }
        
        elif effect == "buff":          # beaver
            if target == "random":
                attack_buff, health_buff = trigger["amount"]
                count = trigger["count"]
                random_idx = self.get_random_indices(count, False)
                for i in random_idx:
                    debug(f"  {self.pets[i]} receiving {attack_buff, health_buff} from {pet}")
                    self.pets[i].receive_buff(attack_buff, health_buff)
        
        trigger.update({
            "gold returned": pet.level()
        })
        return trigger

    def on_friend_buy(self, friend: Animal):
        # handle (single) "on friend buy" ability

        for i, pet in enumerate(self.pets):
            if pet is None:
                continue
            trigger = pet.on_friend_buy(friend)

            if not trigger:
                continue

            if trigger["effect"] == "buff":
                if trigger["target"] == "friends":          # dragon
                    attack_buff, health_buff = trigger["amount"]
                    other_indices = [j for j in range(len(self.pets)) if j != i]

                    for j in other_indices:
                        debug(f"  {self.pets[j]} receiving {attack_buff, health_buff} from {pet}")
                        self.pets[j].receive_buff(attack_buff, health_buff)

    def on_pet_level_up(self, index: int):
        # handle (single) "on level up" ability

        pet = self.pets[index]

        trigger = pet.on_level_up()
        if not trigger:
            return
        
        effect = trigger["effect"]
        target = trigger["target"]

        if effect == "buff":            # fish
            if target == "2":
                attack_buff, health_buff = trigger["amount"]
                random_idx = self.get_random_indices(2, False, index)
                for i in random_idx:
                    debug(f"  {self.pets[i]} receiving {attack_buff, health_buff} from {pet}")
                    self.pets[i].receive_buff(attack_buff, health_buff)

    def on_start_turn(self):
        ret = {}

        for pet in self.pets:
            if not pet:
                continue
            trigger = pet.on_start_turn()

            if trigger:
                ret.update(trigger)

        return ret

    def on_end_turn(self):
        # handle "on end turn" abilities

        pets = [p for p in self.pets if p is not None]
        for index, pet in enumerate(pets):
            if not pet:
                continue
            trigger = pet.on_end_turn()

            if not trigger:
                continue

            effect = trigger["effect"]
            target = trigger["target"]

            if effect == "copy":            # parrot
                if index == 0:      # parrot is at front, no one to copy
                    continue

                copy_pet = pets[index - 1]
                debug(f"  {pet} copying {copy_pet}")
                pet.copy_pet = copy_pet
                continue

            # below effects are all "buff"
            attack_buff, health_buff = trigger['amount']

            if effect == "on loss":         # snail
                if self.lost_last_battle:
                    debug(f"  {pet} giving friends {health_buff} hp")
                    for friend in pets:
                        if friend != pet:
                            friend.receive_buff(0, health_buff)

            elif target == "self":          # bison
                # if team has level 3 friend on it
                has_l3_pet = any(
                    friend is not None and friend.level() == 3 and friend != pet
                    for friend in pets
                )
                if has_l3_pet:
                    pet.receive_buff(attack_buff, health_buff)
                    debug(f"  {pet} gaining {attack_buff, health_buff} --> {pet.get_battle_stats()}")

            elif target == "ahead":         # giraffe
                count = trigger["count"]
                indices_buff = [index - c for c in range(1, count + 1)]
                indices_buff = [i for i in indices_buff if i >= 0]

                for i in indices_buff:
                    pets[i].receive_buff(attack_buff, health_buff)
                    debug(f"  {pet} giving {attack_buff, health_buff} to {pets[i]} --> {pets[i].get_battle_stats()}")

            elif target == "front":         # monkey
                pets[0].receive_buff(attack_buff, health_buff)
                debug(f"  {pet} giving {attack_buff, health_buff} to {pets[0]} --> {pets[0].get_battle_stats()}")

            elif target == "high level":    # penguin
                indices_buff = [
                    i for i in range(len(pets) - 1, -1, -1)         # from last to first
                    if pets[i].level() >= 2
                ]
                indices_buff = indices_buff[:trigger["count"]]

                for i in indices_buff:
                    pets[i].receive_buff(attack_buff, health_buff)
                    debug(f"  {pet} giving {attack_buff, health_buff} to {pets[i]} --> {pets[i].get_battle_stats()}")

