from abc import ABC, abstractmethod
from typing import List

import pygame
import random


class AbstractObject(ABC):
    def __init__(self):
        self.sprite_icon_path = None
        self.__sprite = None
        self.name = None

    def draw(self, display):
        pass

    @property
    def sprite_icon_path(self):
        return self.__sprite_icon_path

    @sprite_icon_path.setter
    def sprite_icon_path(self, sprite_icon_path):
        self.__sprite_icon_path = sprite_icon_path

    @property
    def sprite(self):
        return self.__sprite

    @sprite.setter
    def sprite(self, sprite):
        self.__sprite = sprite

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name


class Interactive(ABC):
    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):
    def __init__(self):
        super().__init__()
        self.action = None
        self.position = None
        self.min_count = None
        self.max_count = None

    @property
    def action(self):
        return self.__action

    @action.setter
    def action(self, action):
        self.__action = action

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position

    @property
    def min_count(self):
        return self.__min_count

    @min_count.setter
    def min_count(self, min_count):
        self.__min_count = min_count

    @property
    def max_count(self):
        return self.__max_count

    @max_count.setter
    def max_count(self, max_count):
        self.__max_count = max_count

    def interact(self, engine, hero):
        self.action(engine, hero)

    def __copy__(self):
        new = self.__class__()
        new.action = self.action
        new.interact = self.interact
        new.sprite = self.sprite
        new.sprite_icon_path = self.sprite_icon_path
        new.name = self.name

        return new


class MagicObject(Ally):
    ...


class Creature(AbstractObject):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats.copy()
        self.__position = None
        self.__max_hp = None
        self.__exp = None
        self.max_hp = self.calc_max_hp()
        self.hp = self.max_hp

    @property
    def stats(self):
        return self.__stats

    @stats.setter
    def stats(self, stats):
        self.__stats = stats

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, hp):
        self.__hp = hp

    @property
    def exp(self):
        return self.__exp

    @exp.setter
    def exp(self, exp):
        self.__exp = exp

    @property
    def max_hp(self):
        return self.__max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.__max_hp = value

    def calc_max_hp(self):
        return 5 + self.stats["endurance"] * 2


class Hero(Creature):
    __BASE_STATS = {
        "strength": 20,
        "endurance": 20,
        "intelligence": 5,
        "luck": 5
    }
    __BASE_POSITION = [1, 1]
    __LEVEL_UP_VALUE = 1
    __STRENGTH_UP_VALUE = 2
    __ENDURANCE_UP_VALUE = 2

    def __init__(self):
        super().__init__(self.__BASE_STATS)
        self.__level = 0
        self.__exp = 0
        self.__exp_to_level_up = 0
        self.__gold = 0
        self.__position = self.__BASE_POSITION

    def calc_exp_to_level_up(self):
        self.exp_to_level_up = 100 * (2 ** (self.level - 1))

    def level_up(self):
        while self.exp >= self.exp_to_level_up:
            self.level += self.__LEVEL_UP_VALUE
            self.calc_exp_to_level_up()
            self.stats["strength"] += self.__STRENGTH_UP_VALUE
            self.stats["endurance"] += self.__ENDURANCE_UP_VALUE
            self.max_hp = self.calc_max_hp()
            self.hp = self.max_hp

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level):
        self.__level = level

    @property
    def exp(self):
        return self.__exp

    @exp.setter
    def exp(self, exp):
        self.__exp = exp

    @property
    def exp_to_level_up(self):
        return self.__exp_to_level_up

    @exp_to_level_up.setter
    def exp_to_level_up(self, exp_to_level_up):
        self.__exp_to_level_up = exp_to_level_up

    @property
    def gold(self):
        return self.__gold

    @gold.setter
    def gold(self, gold):
        self.__gold = gold

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position = position


class Effect(Hero):
    def __init__(self, base):
        super().__init__()
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()
        self.max_hp = self.calc_max_hp()
        self.hp = self.max_hp

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value):
        self.__hp = value

    @property
    def max_hp(self):
        return self.__max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.__max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def exp_to_level_up(self):
        return self.base.exp_to_level_up

    @exp_to_level_up.setter
    def exp_to_level_up(self, value):
        self.base.exp_to_level_up = value

    @property
    def sprite(self):
        return self.base.sprite

    @sprite.setter
    def sprite(self, sprite):
        self.base.sprite = sprite

    @abstractmethod
    def apply_effect(self):
        pass


class Berserk(Effect):
    def apply_effect(self):
        self.stats["strength"] += 7
        self.stats["endurance"] += 7
        self.stats["intelligence"] -= 3


class Blessing(Effect):
    def apply_effect(self):
        self.stats["strength"] += 2
        self.stats["endurance"] += 2
        self.stats["intelligence"] += 2
        self.stats["luck"] += 2


class Weakness(Effect):
    def apply_effect(self):
        self.stats["strength"] -= 4
        self.stats["endurance"] -= 4


class Enemy(Creature, Interactive):
    def __init__(self, enemy_dict):
        super().__init__(enemy_dict)
        self.exp = enemy_dict.get('experience')

    def interact(self, engine, hero):
        if self.fight(engine, hero):
            engine.notify("you've beaten {}".format(self.name))
            hero.exp += self.exp
        else:
            engine.game_over = True

    def fight(self, engine, hero):
        hero_strength = hero.stats['strength']
        enemy_strength = self.stats['strength']
        while True:
            hero.hp -= enemy_strength
            engine.notify('{} strikes with {} hp'.format(self.name,
                                                         enemy_strength))
            self.hp -= hero_strength
            engine.notify('you strike with {} hp'.format(hero_strength))
            if hero.hp < 0:
                return False
            if self.hp < 0:
                return True

    def __copy__(self):
        new = self.__class__(self.stats)
        new.interact = self.interact
        new.fight = self.fight
        new.exp = self.exp
        new.stats = self.stats
        new.sprite = self.sprite
        new.sprite_icon_path = self.sprite_icon_path
        new.name = self.name
        new.position = self.position
        new.calc_max_hp = self.calc_max_hp
        new.hp = self.max_hp

        return new


class PrototypeList:
    def __init__(self):
        self.objects = []  # type: List[MagicObject]
        self.allies = []  # type: List[Ally]
        self.enemies = []  # type: List[Enemy]

    @staticmethod
    def __get_by_name(collection, name):
        for instance in collection:
            if instance.name == name:
                return instance

        return None

    def get_object_by_name(self, name) -> MagicObject:
        object_prototype = self.__get_by_name(self.objects, name)
        if not object_prototype:
            object_prototype = MagicObject()
            object_prototype.name = name
            self.objects.append(object_prototype)

        return object_prototype

    def get_ally_by_name(self, name) -> Ally:
        ally_prototype = self.__get_by_name(self.allies, name)
        if not ally_prototype:
            ally_prototype = Ally()
            ally_prototype.name = name
            self.allies.append(ally_prototype)

        return ally_prototype

    def get_enemy_by_name(self, name, stats=None) -> Enemy:
        enemy_prototype = self.__get_by_name(self.enemies, name)
        if not enemy_prototype:
            enemy_prototype = Enemy(stats)
            enemy_prototype.name = name
            self.enemies.append(enemy_prototype)

        return enemy_prototype
