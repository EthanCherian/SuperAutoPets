from typing import Dict
import copy

from objects.animal import Animal
from utils.helpers import debug, error, warning, success
from utils.helpers import get_random_pet_from_tiers

# TIER 1 ANIMALS
class Cricket(Animal):
    zomb_attack = [1, 2, 3]
    zomb_health = [1, 2, 3]

    def __init__(self):
        super().__init__("cricket")
    
    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        # summon zombie cricket
        z = Animal("zombie cricket", self.exp, self.zomb_attack[l], self.zomb_health[l])
        # debug(f"{self} fainted, summoning {z} @ {z.get_battle_stats()}")
        ret.update({
            "img": str(self),
            "effect": "summon",
            "target": "team",
            "token": z,
            "count": 1
        })

        return ret

class Fish(Animal):
    atk_buff = [1, 2]
    hp_buff = [1, 2]

    def __init__(self):
        super().__init__("fish")
    
    def on_level_up(self):
        l = self.level() - 2
        return {
            "img": str(self),
            "effect": "buff",
            "target": "2",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

class Horse(Animal):
    attack_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("horse")

    def on_friend_summon(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "friend",
            "amount": (self.attack_buff[l], 0),
            "temporary": True
        }
        # friend.receive_buff(self.attack_buff[l], 0, temporary=True)
        # debug(f"{self} giving {self.attack_buff[l]} attack to summoned {friend} @ {friend.get_battle_stats()}")

class Ant(Animal):
    attack_buff = [1, 2, 3]
    health_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("ant")

    def on_faint(self):
        ret = super().on_faint() 

        l = self.level() - 1
        ret.update({
            "img": str(self),
            "effect": "buff",
            "target": "random",
            "amount": (self.attack_buff[l], self.health_buff[l])
        })
        
        return ret

class Beaver(Animal):
    buff_cnt: int = 2
    attack_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("beaver")
    
    def on_sell(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "random",
            "amount": (self.attack_buff[l], 0),
            "count": self.buff_cnt
        }

class Duck(Animal):
    hp_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("duck")
    
    def on_sell(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "shop",
            "amount": (0, self.hp_buff[l])
        }

class Mosquito(Animal):
    damage: int = 1
    dmg_count = [1, 2, 3]

    def __init__(self):
        super().__init__("mosquito")
    
    def on_battle_start(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "damage",
            "target": "random",
            "damage": self.damage,
            "count": self.dmg_count[l]
        }

class Otter(Animal):
    health_buff: int = 1
    buff_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("otter")

    def on_buy(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "random",
            "amount": (0, self.health_buff),
            "count": self.buff_cnt[l]
        }

class Pig(Animal):
    gold = [1, 2, 3]

    def __init__(self):
        super().__init__("pig")
    
    def on_sell(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "gold",
            "target": "shop",
            "amount": self.gold[l]
        }

class Pigeon(Animal):
    crumb_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("pigeon")
    
    def on_sell(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "stock",
            "target": "food",
            "food": "bread crumbs",
            "amount": self.crumb_cnt[l]
        }

# TIER 2 ANIMALS
class Crab(Animal):
    health_pct = [0.5, 1, 1.5]

    def __init__(self):
        super().__init__("crab")
    
    def on_battle_start(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "copy",
            "target": "health",
            "amount": self.health_pct[l]
        }

class Flamingo(Animal):
    attack_buff = [1, 2, 3]
    health_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("flamingo")

    def on_faint(self):
        ret = super().on_faint()
        
        l = self.level() - 1
        ret.update({
            "img": str(self),
            "effect": "buff",
            "target": "2",
            "amount": (self.attack_buff[l], self.health_buff[l])
        })

        return ret

class Hedgehog(Animal):
    dmg = [2, 4, 6]

    def __init__(self):
        super().__init__("hedgehog")
    
    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        ret.update({
            "img": str(self),
            "effect": "damage",
            "target": "all",
            "amount": self.dmg[l]
        })
        
        return ret

class Kangaroo(Animal):
    attack_buff = [1, 2, 3]
    health_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("kangaroo")
    
    def on_friend_ahead_attack(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "self",
            "amount": (self.attack_buff[l], self.health_buff[l])
        }
        # self.receive_buff(self.attack_buff[l], self.health_buff[l], temporary=True)
        # debug(f"  {self} gaining ({self.attack_buff[l]}, {self.health_buff[l]}) --> ({self.battle_attack}, {self.battle_health})")

class Peacock(Animal):
    attack_buff = [4, 8, 12]

    def __init__(self):
        super().__init__("peacock")
    
    def on_hurt(self, other_attack: int, attacker: Animal = None):
        l = self.level() - 1
        curr_health = self.battle_health
        super().on_hurt(other_attack, attacker)
        new_health = self.battle_health

        ret = None
        if new_health != curr_health:       # actually got hurt
            ret = {
                "img": str(self),
                "effect": "buff",
                "target": "self",
                "amount": (self.attack_buff[l], 0)
            }
        return ret

class Rat(Animal):
    dirty_count = [1, 2, 3]

    def __init__(self):
        super().__init__("rat")
    
    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        d = Animal("dirty rat")
        # debug(f"{self} fainted, summoning {d} @ {d.get_battle_stats()}")
        ret.update({
            "img": str(self),
            "effect": "summon",
            "target": "enemy",
            "token": d,
            "count": self.dirty_count[l]
        })

        return ret

class Snail(Animal):
    hp_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("snail")
    
    def on_end_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "on loss",
            "target": "team",
            "amount": (0, self.hp_buff[l])
        }

class Spider(Animal):
    tkn_attack = [2, 4, 6]
    tkn_health = [2, 4, 6]
    tkn_level = [1, 2, 3]

    def __init__(self):
        super().__init__("spider")
    
    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        name = get_random_pet_from_tiers([3])[0]
        token = copy.copy(CREATE_PET[name])
        # debug(f"{self} fainted, summoning {token} @ {self.tkn_attack[l], self.tkn_health[l]}")
        token.set_stats(self.tkn_attack[l], self.tkn_health[l])
        token.set_level(self.tkn_level[l])

        ret.update({
            "img": str(self),
            "effect": "summon",
            "target": "team",
            "token": token,
            "count": 1
        })

        return ret

class Swan(Animal):
    gold_gain = [1, 2, 3]

    def __init__(self):
        super().__init__("swan")

    def on_start_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "gold": self.gold_gain[l]
        }

class Worm(Animal):
    apple_stock = ["apple", "better apple", "best apple"]

    def __init__(self):
        super().__init__("worm")

    def on_start_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "stock": self.apple_stock[l]
        }

# TIER 3 ANIMALS
class Dodo(Animal):
    attack_pct = [0.5, 1, 1.5]

    def __init__(self):
        super().__init__("dodo")

    def on_battle_start(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "attack",
            "amount": self.attack_pct[l]
        }

class Badger(Animal):
    damage_pct = [0.5, 1, 1.5]

    def __init__(self):
        super().__init__("badger")

    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        ret.update({
            "img": str(self),
            "effect": "damage",
            "target": "adjacent",
            "damage": int(self.damage_pct[l] * self.battle_attack)
        })

        return ret

class Dolphin(Animal):
    damage_cnt = [1, 2, 3]
    damage: int = 4

    def __init__(self):
        super().__init__("dolphin")

    def on_battle_start(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "damage",
            "target": "lowest",
            "damage": self.damage,
            "count": self.damage_cnt[l]
        }

class Giraffe(Animal):
    buff = (1, 1)
    buff_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("giraffe")

    def on_end_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "ahead",
            "amount": self.buff,
            "count": self.buff_cnt[l]
        }

class Elephant(Animal):
    damage = 1
    dmg_count = [1, 2, 3]

    def __init__(self):
        super().__init__("elephant")
    
    def after_attack(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "damage",
            "target": "behind",
            "damage": self.damage,
            "count": self.dmg_count[l]
        }

class Camel(Animal):
    attack_buff = [1, 2, 3]
    health_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("camel")
    
    def on_hurt(self, other_attack: int, attacker: Animal = None):
        l = self.level() - 1
        curr_health = self.battle_health
        super().on_hurt(other_attack, attacker)
        new_health = self.battle_health

        ret = None
        if new_health != curr_health:       # actually got hurt
            ret = {
                "img": str(self),
                "effect": "buff",
                "target": "behind",
                "amount": (self.attack_buff[l], self.health_buff[l])
            }
        return ret

class Rabbit(Animal):
    health_buffs = [1, 2, 3]

    def __init__(self):
        super().__init__("rabbit")

    def on_friend_eats_food(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "ate",
            "amount": (0, self.health_buffs[l])
        }

class Ox(Animal):
    trigger_cnt = [1, 2, 3]
    curr_cnt = 0
    attack_buff = 1

    def __init__(self):
        super().__init__("ox")
    
    def on_start_turn(self):
        self.curr_cnt = 0

    def on_friend_ahead_faints(self):
        l = self.level() - 1
        if self.curr_cnt < self.trigger_cnt[l]:
            self.curr_cnt += 1
            
            return {
                "img": str(self),
                "effect": "buff",
                "target": "self",
                "amount": (self.attack_buff, 0),
                "perk": 7
            }

class Dog(Animal):
    attack_buff = [2, 4, 6]
    health_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("dog")

    def on_friend_summon(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "self",
            "amount": (self.attack_buff[l], self.health_buff[l])
        }
        # self.receive_buff(self.attack_buff[l], self.health_buff[l], temporary=True)
        # debug(f"  {self} gaining {self.attack_buff[l], self.health_buff[l]} --> {self.battle_attack, self.battle_health}")

class Sheep(Animal):
    ram_count: int = 2
    ram_attack = [2, 4, 6]
    ram_health = [2, 4, 6]

    def __init__(self):
        super().__init__("sheep")
    
    def on_faint(self):
        l = self.level() - 1
        r = Animal("ram", self.exp, self.ram_attack[l], self.ram_health[l])
        # debug(f"{self} fainted, summoning 2x {r} @ {r.get_battle_stats()}")
        return {
            "img": str(self),
            "effect": "summon",
            "target": "team",
            "token": r,
            "count": self.ram_count
        }

# TIER 4 ANIMALS
class Skunk(Animal):
    health_decr = [0.333, 0.666, 0.999]

    def __init__(self):
        super().__init__("skunk")

    def on_battle_start(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "debuff",
            "target": "health",
            "amount": self.health_decr[l]
        }

class Hippo(Animal):
    atk_buff = [2, 4, 6]
    hp_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("hippo")

    def on_knockout(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "self",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

class Bison(Animal):
    atk_buff = [1, 2, 3]
    hp_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("bison")

    def on_end_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "self",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

class Blowfish(Animal):
    damage = [3, 6, 9]

    def __init__(self):
        super().__init__("blowfish")

    def on_hurt(self, other_attack: int, attacker: Animal = None):
        l = self.level() - 1
        curr_health = self.battle_health
        super().on_hurt(other_attack, attacker)
        new_health = self.battle_health

        ret = None
        if curr_health != new_health:
            ret = {
                "img": str(self),
                "effect": "damage",
                "target": "random",
                "damage": self.damage[l]
            }
        return ret

class Turtle(Animal):
    melon_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("turtle")

    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        ret.update({
            "img": str(self),
            "effect": "perk",
            "target": "behind",
            "perk": 7,
            "count": self.melon_cnt[l]
        })

        return ret

class Squirrel(Animal):
    savings = [1, 2, 3]

    def __init__(self):
        super().__init__("squirrel")

    def on_start_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "shop": self.savings[l]
        }

class Penguin(Animal):
    atk_buff = [1, 2, 3]
    hp_buff = [1, 2, 3]
    buff_cnt = 2

    def __init__(self):
        super().__init__("penguin")

    def on_end_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "high level",
            "amount": (self.atk_buff[l], self.hp_buff[l]),
            "count": self.buff_cnt
        }

class Deer(Animal):
    bus_atk = [5, 10, 15]
    bus_hp = [5, 10, 15]
    bus_lvl = [1, 2, 3]

    def __init__(self):
        super().__init__("deer")

    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        # summon bus
        b = Animal("bus", self.exp, self.bus_atk[l], self.bus_hp[l])
        b.set_level(self.bus_lvl[l])
        # b.receive_perk(5)
        # debug(f"{self} fainted, summoning {b} @ {b.get_battle_stats()}")
        ret.update({
            "img": str(self),
            "effect": "summon",
            "target": "team",
            "token": b,
            "count": 1
        })

        return ret

class Whale(Animal):
    summon_lvl = [1, 2, 3]
    summon_pet: Animal = None

    def __init__(self):
        super().__init__("whale")

    def on_start_turn(self):
        self.summon_pet = None
    
    def on_battle_start(self):
        return {
            "img": str(self),
            "effect": "faint",
            "target": "ahead"
        }

    def on_faint(self):
        ret = super().on_faint()
        l = self.level() - 1

        if self.summon_pet is not None:
            self.summon_pet.set_level(self.summon_lvl[l])
            self.summon_pet.prepare_battle()
            # debug(f"{self} fainted, summoning {self.summon_pet} @ {self.summon_pet.get_battle_stats()}")
            ret.update({
                "img": str(self),
                "effect": "summon",
                "target": "team",
                "token": self.summon_pet,
                "count": 1
            })

        return ret

class Parrot(Animal):
    copy_pet: Animal = None
    copy_lvl = [1, 2, 3]

    def __init__(self):
        super().__init__("parrot")
    
    def reset(self):
        self.copy_pet = None
        super().reset()

    def on_end_turn(self):
        return {
            "img": str(self),
            "effect": "copy",
            "target": "ahead",
        }
    
    def on_battle_start(self):
        # ensure copy_pet is properly set up to trigger it's abilities in battle

        # get fresh copy of pet (not technically necessary i think)
        self.copy_pet = GET_PET(self.copy_pet.name)

        l = self.level() - 1
        self.copy_pet.set_level(self.copy_lvl[l])

        # trigger copy_pet's battle_start ability (if any)
        return self.copy_pet.on_battle_start()
    
    # all triggers that parrot can activate are in battle, below

    def on_friend_summon(self):
        # turkey, horse - work independently
        return self.copy_pet.on_friend_summon()

    def on_faint(self):
        # so many fuckers >:(
        # this one requires a relatively major overhaul I predict
        return self.copy_pet.on_faint()

    def on_knockout(self):
        # rhino - works independently
        # hippo - need to fix
        return self.copy_pet.on_knockout()

    def on_hurt(self, other_attack: int, attacker: Animal = None):
        # peacock, camel, blowfish, gorilla
        # this one requires an insane amount of overhaul tbh
        return self.copy_pet.on_hurt(other_attack, attacker)

    def before_attack(self):
        # boar
        return self.copy_pet.before_attack()

    def after_attack(self):
        # elephant - works independently
        return self.copy_pet.after_attack()

    def on_friend_ahead_attack(self):
        return self.copy_pet.on_friend_ahead_attack()

    def on_friend_ahead_faints(self):
        return self.copy_pet.on_friend_ahead_faints()

    def on_friend_faint(self):
        return self.copy_pet.on_friend_faint()

# TIER 5 ANIMALS
class Scorpion(Animal):
    # i legit think this one will work on its own
    # comes with inherent peanut perk from constants
    # ensures 1-up, whale, etc. all work as intended

    def __init__(self):
        super().__init__("scorpion")

class Crocodile(Animal):
    damage = 8
    dmg_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("crocodile")

    def on_battle_start(self):
        l = self.level() - 1

        return {
            "img": str(self),
            "effect": "damage",
            "target": "last",
            "damage": self.damage,
            "count": self.dmg_cnt[l]
        }

class Rhino(Animal):
    damage = [4, 8, 12]

    def __init__(self):
        super().__init__("rhino")

    def on_knockout(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "damage",
            "target": "next",
            "damage": self.damage[l]
        }

class Monkey(Animal):
    atk_buff = [2, 4, 6]
    hp_buff = [3, 6, 9]

    def __init__(self):
        super().__init__("monkey")

    def on_end_turn(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "front",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

class Armadillo(Animal):
    hp_buff = [8, 16, 24]

    def __init__(self):
        super().__init__("armadillo")

    def on_battle_start(self):
        l = self.level() - 1

        return {
            "img": str(self),
            "effect": "buff",
            "target": "all",
            "amount": (0, self.hp_buff[l])
        }

class Cow(Animal):
    milk_stock = ["milk", "better milk", "best milk"]

    def __init__(self):
        super().__init__("cow")

    def on_buy(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "stock",
            "target": "shop",
            "stock": self.milk_stock[l]
        }

class Seal(Animal):
    atk_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("seal")

    def on_food_eaten(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "3",
            "amount": self.atk_buff[l]
        }

class Rooster(Animal):
    dmg_pct: float = 0.5
    chick_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("rooster")

    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1
        c = Animal("chick", self.exp)
        c.set_stats(int(self.dmg_pct * self.battle_attack), 1)
        # debug(f"{self} fainted, summoning {self.chick_cnt[l]}x {c} @ {c.get_battle_stats()}")
        ret.update({
            "img": str(self),
            "effect": "summon",
            "target": "team",
            "token": c,
            "count": self.chick_cnt[l]
        })

        return ret

class Shark(Animal):
    atk_buff = [2, 4, 6]
    hp_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("shark")

    def on_friend_faint(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "self",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

class Turkey(Animal):
    atk_buff = [3, 6, 9]
    hp_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("turkey")

    def on_friend_summon(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "friend",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

# TIER 6 ANIMALS
class Leopard(Animal):
    damage_pct: float = 0.5
    damage_cnt = [1, 2, 3]

    def __init__(self):
        super().__init__("leopard")

    def on_battle_start(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "damage",
            "target": "random",
            "damage": int(self.damage_pct * self.battle_attack),
            "count": self.damage_cnt[l]
        }

class Boar(Animal):
    attack_buff = [4, 8, 12]
    health_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("boar")
    
    def before_attack(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "self",
            "amount": (self.attack_buff[l], self.health_buff[l])
        }
        # self.receive_buff(self.attack_buff[l], self.health_buff[l], temporary=True)
        # debug(f"  {self} gaining ({self.attack_buff[l]}, {self.health_buff[l]}) --> ({self.battle_attack}, {self.battle_health})")

class Tiger(Animal):
    def __init__(self):
        super().__init__("tiger")

    def on_friend_ability(self):            # TODO: create super function (or don't lol)
        pass

class Wolverine(Animal):
    def __init__(self):
        super().__init__("wolverine")

    def on_friend_ability(self):            # TODO: create super function (or don't lol)
        pass

class Gorilla(Animal):
    perk_cnt = [1, 2, 3]
    curr_cnt = 0

    def __init__(self):
        super().__init__("gorilla")
    
    def reset(self):
        self.curr_cnt = 0
        super().reset()

    def on_hurt(self, other_attack: int, attacker: Animal = None):
        curr_health = self.battle_health
        super().on_hurt(other_attack, attacker)
        if self.battle_health >= curr_health:
            return
        
        l = self.level() - 1
        if self.curr_cnt < self.perk_cnt[l]:
            # debug(f"  {self} hurt, gaining coconut")
            # TODO: this should prob be done in team, not here; armor need not always be temporary
            # self.receive_perk(11, temporary=True)       # give coconut
            self.curr_cnt += 1
            return {
                "img": str(self),
                "effect": "perk",
                "target": "self",
                "perk": 11
            }

class Dragon(Animal):
    atk_buff = [1, 2, 3]
    hp_buff = [1, 2, 3]

    def __init__(self):
        super().__init__("dragon")

    def on_friend_buy(self, friend: Animal):
        if friend.tier != 1:
            return

        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "buff",
            "target": "friends",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        }

class Mammoth(Animal):
    atk_buff = [2, 4, 6]
    hp_buff = [2, 4, 6]

    def __init__(self):
        super().__init__("mammoth")

    def on_faint(self):
        ret = super().on_faint()

        l = self.level() - 1

        ret.update({
            "img": str(self),
            "effect": "buff",
            "target": "friends",
            "amount": (self.atk_buff[l], self.hp_buff[l])
        })
        return ret

class Cat(Animal):
    food_inc_pct = [1, 2, 3]
    mult_cnt = 2

    def __init__(self):
        super().__init__("cat")

    def on_start_turn(self):
        super().on_start_turn()
        self.mult_cnt = 2

    def on_friend_eats_food(self):
        l = self.level() - 1
        if self.mult_cnt > 0:
            self.mult_cnt -= 1
            return {
                "img": str(self),
                "effect": "increase",
                "target": "ate",
                "amount": self.food_inc_pct[l]
            }

class Snake(Animal):
    damage = [5, 10, 15]

    def __init__(self):
        super().__init__("snake")

    def on_friend_ahead_attack(self):
        l = self.level() - 1
        return {
            "img": str(self),
            "effect": "damage",
            "target": "random",
            "amount": self.damage[l]
        }

class Fly(Animal):
    zomb_atk = [4, 8, 12]
    zomb_hp = [4, 8, 12]
    summon_cnt = 3

    def __init__(self):
        super().__init__("fly")
    
    def on_start_turn(self):
        self.summon_cnt = 3

    def on_friend_faint(self):
        l = self.level() - 1

        if self.summon_cnt > 0:
            f = Animal("zombie fly", self.exp, self.zomb_atk[l], self.zomb_hp[l])

            return {
                "img": str(self),
                "effect": "summon",
                "target": "team",
                "token": f,
                "count": 1
            }
    
    def summon_msg(self, f: Animal):
        self.summon_cnt -= 1
        # debug(f"  {self} summoning {f} @ {f.get_battle_stats()}, {self.summon_cnt} remaining")


# ----------------------------------------------------------

# map from pet name to pet object
CREATE_PET: Dict[str, Animal] = {
    "bee": Animal("bee"),
    "zombie cricket": Animal("zombie cricket"),
    "dirty rat": Animal("dirty rat"),
    "ram": Animal("ram"),
    "bus": Animal("bus"),
    "chick": Animal("chick"),
    "zombie fly": Animal("zombie fly"),
    
    "cricket": Cricket(),
    "fish": Fish(),
    "horse": Horse(),
    "ant": Ant(),
    "beaver": Beaver(),
    "duck": Duck(),
    "mosquito": Mosquito(),
    "otter": Otter(),
    "pig": Pig(),
    "pigeon": Pigeon(),
    
    "crab": Crab(),
    "flamingo": Flamingo(),
    "hedgehog": Hedgehog(),
    "kangaroo": Kangaroo(),
    "peacock": Peacock(),
    "rat": Rat(),
    "snail": Snail(),
    "spider": Spider(),
    "swan": Swan(),
    "worm": Worm(),

    "dodo": Dodo(),
    "badger": Badger(),
    "dolphin": Dolphin(),
    "giraffe": Giraffe(),
    "elephant": Elephant(),
    "camel": Camel(),
    "rabbit": Rabbit(),
    "ox": Ox(),
    "dog": Dog(),
    "sheep": Sheep(),

    "skunk": Skunk(),
    "hippo": Hippo(),
    "bison": Bison(),
    "blowfish": Blowfish(),
    "turtle": Turtle(),
    "squirrel": Squirrel(),
    "penguin": Penguin(),
    "deer": Deer(),
    "whale": Whale(),
    "parrot": Parrot(),

    "scorpion": Scorpion(),
    "crocodile": Crocodile(),
    "rhino": Rhino(),
    "monkey": Monkey(),
    "armadillo": Armadillo(),
    "cow": Cow(),
    "seal": Seal(),
    "rooster": Rooster(),
    "shark": Shark(),
    "turkey": Turkey(),

    "leopard": Leopard(),
    "boar": Boar(),
    "tiger": Tiger(),
    "wolverine": Wolverine(),
    "gorilla": Gorilla(),
    "dragon": Dragon(),
    "mammoth": Mammoth(),
    "cat": Cat(),
    "snake": Snake(),
    "fly": Fly(),
}

def GET_PET(name: str) -> Animal:
    # get a clean copy of the pet object matching name
    return copy.copy(CREATE_PET[name])