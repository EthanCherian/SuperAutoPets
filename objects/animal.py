from __future__ import annotations
from utils.constants import PETS, PET_NAMES, PET_EMOJIS
from utils.constants import PERK_EMOJIS, PERKS
from utils.constants import USE_EMOJI

# import number of cans used (from game?) and use to upgrade base stats

class Animal:
    name: str = ""
    tier: int = 0
    exp: int = -1
    attack: int = 0
    health: int = 0
    perk: int = 0
    battle_attack: int = 0
    battle_health: int = 0
    battle_perk: int = 0

    cost: int = 0

    def __init__(self, name, exp=0, attack=0, health=0):
        self.name = name
        self.initialize_stats(exp, attack, health)
        self.cost = 3

    def initialize_stats(self, exp=0, attack=0, health=0):
        loc = PET_NAMES.index(self.name)
        base_pet = PETS[loc]

        self.tier = base_pet["tier"]
        self.exp = max(exp, base_pet["exp"])
        self.perk = base_pet["perk"]
        self.attack = max(attack, base_pet["attack"])
        self.health = max(health, base_pet["health"])

        self.battle_attack = self.attack
        self.battle_health = self.health

    def set_stats(self, attack, health):
        self.attack = attack
        self.health = health

        self.attack = min(self.attack, 50)      # don't scale over 50
        self.health = min(self.health, 50)

        self.battle_attack = attack
        self.battle_health = health

    def set_level(self, level=1, exp=0, scale_stats=True):
        # desired_level = level if level > 1 else self.level(exp)
        desired_level = min(level, 3)
        
        curr_level = self.level()
        while desired_level != curr_level:
            self.exp += 1       # gain 1 exp at a time
            if scale_stats:
                self.receive_buff(1, 1)
            
            if self.level() != curr_level:
                self.on_level_up()

            curr_level = self.level()

    def __str__(self):
        if USE_EMOJI:
            return f"{PET_EMOJIS[self.name]}"
        return f"{self.name}"

    def reset(self):
        self.battle_attack = self.attack
        self.battle_health = self.health
        self.battle_perk = self.perk

    def get_stats(self):
        return (self.name, self.tier, self.exp, self.perk, self.attack, self.health)

    def get_battle_stats(self):
        if self.battle_perk == 0:
            return (self.battle_attack, self.battle_health)
        return (self.battle_attack, self.battle_health, PERK_EMOJIS[PERKS[self.battle_perk]])
    
    def get_info(self, battle=False):
        if battle:
            return (self.name, self.exp, self.level(), self.battle_perk, self.battle_attack, self.battle_health)
        return (self.name, self.exp, self.level(), self.perk, self.attack, self.health)

    def prepare_battle(self):
        self.attack = min(self.attack, 50)      # don't scale over 50
        self.health = min(self.health, 50)

        self.battle_attack = max(self.attack, self.battle_attack)
        self.battle_health = max(self.health, self.battle_health)
        self.battle_perk = self.perk

    def receive_buff(self, attack_buff: int, health_buff: int, temporary: bool = False):
        if not temporary:
            self.attack += attack_buff
            self.health += health_buff
        
            self.attack = min(self.attack, 50)      # don't scale over 50
            self.health = min(self.health, 50)

        self.battle_attack += attack_buff
        self.battle_health += health_buff
        self.battle_attack = min(self.battle_attack, 50)      # don't scale over 50
        self.battle_health = min(self.battle_health, 50)

    def receive_perk(self, perk: int, temporary: bool = False):
        if not temporary:
            self.perk = perk
        self.battle_perk = perk

    def combine(self, other: Animal):
        if self.name != other.name:
            print("Can't combine different pets!")
            return
        if self.level() == 3:
            print(f"{self} has reached max level!")
            return

        max_attack = max(self.attack, other.attack)
        max_health = max(self.health, other.health)

        max_exp = max(self.exp, other.exp)
        # TODO: implement combination of statted pets

        if other.perk != 0 and self.perk == 0:
            self.perk = other.perk

        self.attack = max_attack + 1
        self.health = max_health + 1
        self.prepare_battle()

        level = self.level()
        self.exp += other.exp + 1
        if self.level() > level:
            self.on_level_up()
    
    def gain_exp(self, exp_gain: int):
        if self.level() == 3:
            print(f"{self} has reached max level!")
            return
        self.exp += exp_gain
        self.receive_buff(exp_gain, exp_gain)

    def level(self, exp=-1):
        e = exp if exp > 0 else self.exp

        if e >= 5:           # 5 exp :: level 3
            e = 5            # exp caps at 5
            return 3
        
        if e >= 2:           # 2 exp :: level 2
            return 2
        
        return 1                    # otherwise, level 1
    
    def exp_to_next_level(self):
        curr_level = self.level()
        if curr_level == 3:
            return 0
        if curr_level == 2:
            return 5 - self.exp
        return 2 - self.exp

    # events, to be handled separately by each pet
    def on_buy(self):
        pass

    def on_sell(self):
        pass

    def on_level_up(self):
        pass

    def on_battle_start(self):
        pass

    def on_friend_summon(self):
        pass

    def on_faint(self):
        ret = {}
        if self.perk == 1:          # honey
            ret = {
                "honey": True
            }
        elif self.perk == 8:        # mushroom
            ret = {
                "mushroom": True
            }
        
        return ret

    def on_knockout(self):
        pass

    def on_start_turn(self):
        pass

    def on_end_turn(self):
        pass

    def on_hurt(self, other_attack: int, attacker: Animal = None):
        # handle damage reduction (ie. garlic, melon, coconut?, etc. here)
        dmg = other_attack
        other_perk = 0
        if attacker:
            other_perk = attacker.battle_perk

        if other_perk == 3:         # meat
            dmg += 3
            print(f"{attacker} deals 5 more damage with {PERK_EMOJIS[PERKS[other_perk]]} !")
        elif other_perk == 9:       # steak
            dmg += 20
            print(f"{attacker} deals 20 more damage with {PERK_EMOJIS[PERKS[other_perk]]} , which breaks!")
            attacker.battle_perk = 0

        if self.battle_perk == 4:          # garlic
            dmg -= 2
            dmg = max(dmg, 1)           # always take some damage
            print(f"{self}'s {PERK_EMOJIS[PERKS[self.battle_perk]]} reduces damage by 2!")
        elif self.battle_perk == 7:        # melon
            dmg -= 20
            print(f"{self}'s {PERK_EMOJIS[PERKS[self.battle_perk]]} reduces damage by 20 and breaks!")
            self.battle_perk = 0
        
        dmg = max(dmg, 0)
        
        if self.battle_perk == 11:         # coconut (absolute)
            dmg = 0
            print(f"{self}'s {PERK_EMOJIS[PERKS[self.battle_perk]]} prevents damage and breaks!")
            self.battle_perk = 0

        if other_perk == 10 and dmg > 0:        # peanut
            dmg = 100               # insta-kill
            print(f"{self} is knocked out by {attacker}'s {PERK_EMOJIS[PERKS[other_perk]]} !")
        
        self.battle_health -= dmg
    
    def before_attack(self):
        pass

    def after_attack(self):
        pass

    def on_friend_ahead_attack(self):
        pass

    def on_friend_eats_food(self):
        pass

    def on_food_eaten(self):
        pass

    def on_friend_ahead_faints(self):
        pass

    def on_friend_faint(self):
        pass

    def on_friend_buy(self, friend: Animal):
        pass

    def on_friend_ability(self):
        pass
