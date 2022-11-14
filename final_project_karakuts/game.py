from random import randint

import pygame
import objects
from logic import GameEngine
from objects import Blessing, Berserk
from screen_engine import GameSurface, ProgressBar, InfoWindow, \
    HelpWindow, ScreenHandle, GameOverWindow
from service import Service
from sprite import SpriteFactory


class GameActions:
    def __init__(self, game):
        self.game = game

    def get_action_by_name(self, action_name):
        object_list_actions = {'reload_game': self.reload_game,
                               'add_gold': self.add_gold,
                               'apply_blessing': self.apply_blessing,
                               'remove_effect': self.remove_effect,
                               'restore_hp': self.restore_hp}

        return object_list_actions.get(action_name)

    def reload_game(self, engine, hero):
        level_list_max = len(self.game.level_list) - 1
        engine.level += 1
        engine.hero.level_up()
        hero.position = [1, 1]
        engine.objects = []
        generator = self.game.level_list[min(engine.level, level_list_max)]

        map_factory = generator['map']
        map_factory.add_service(engine.service)

        game_map = map_factory.get_map()

        engine.load_map(game_map)

        obj_factory = generator['obj']
        obj_factory.add_service(engine.service)

        engine.add_objects(obj_factory.get_objects(game_map))
        engine.add_size(self.game.size)
        engine.redraw_objects()
        engine.redraw_surface()

    @staticmethod
    def restore_hp(engine, hero):
        engine.score += 0.1
        hero.hp = hero.max_hp
        engine.notify("HP restored")

    def apply_blessing(self, engine, hero):
        gold_amount = self.__calc_gold_amount(engine.level, hero, 20)
        if hero.gold >= gold_amount:
            engine.score += 0.2
            hero.gold -= gold_amount
            if randint(0, 1) == 0:
                engine.hero = Blessing(hero)
                engine.notify("Blessing applied")
            else:
                engine.hero = Berserk(hero)
                engine.notify("Berserk applied")
        else:
            engine.notify("not enough gold for blessing!")
            engine.score -= 0.1

    def remove_effect(self, engine, hero):
        gold_amount = self.__calc_gold_amount(engine.level, hero, 10)
        if hero.gold >= gold_amount and "base" in dir(hero):
            hero.gold -= gold_amount
            engine.notify("Effect {} is removed".format(
                engine.hero.__class__.__name__))
            engine.hero = hero.base
            engine.hero.max_hp = engine.hero.calc_max_hp()
        elif "base" in dir(hero):
            engine.notify("not enough gold for removing effect!")
        else:
            engine.notify("no effects applied to hero")

    @staticmethod
    def __calc_gold_amount(level, hero, coefficient):
        return int(coefficient * 1.5**level) - 2*hero.stats["intelligence"]

    @staticmethod
    def add_gold(engine, hero):
        if randint(1, 10) == 1:
            engine.score -= 0.05
            engine.hero = objects.Weakness(hero)
            engine.notify("You were cursed")
        else:
            engine.score += 0.1
            gold = int(randint(10, 1000) * (1.1**(engine.hero.level-1)))
            hero.gold += gold
            engine.notify(f"{gold} gold added")


class Game:
    __DEFAULT_SIZE = 60
    __MIN_SIZE = 16
    __DEFAULT_ITERATION = 0
    __SIZE_CHANGE = 2
    __ITERATION_CHANGE = 1

    def __init__(self, size=__DEFAULT_SIZE):
        self.size = size
        self.sprite_factory = SpriteFactory()
        self.hero = objects.Hero()
        self.hero.sprite = \
            self.sprite_factory.get_sprite_for_object(self.hero)
        self.hero.sprite.redraw(self.size)
        self.engine = GameEngine(self.hero, Service(self))

        self.drawer = self.__get_drawer_chain()
        self.drawer.connect_engine(self.engine)

        self.level_list = []
        self.actions = GameActions(self)
        self.engine.service.service_init()
        self.actions.reload_game(self.engine, self.hero)
        self.iteration = self.__DEFAULT_ITERATION

    @staticmethod
    def __get_drawer_chain():
        screen_handle = ScreenHandle((0, 0))
        game_over_window = GameOverWindow((700, 500), (0, 0),
                                          screen_handle, pygame.SRCALPHA)
        help_window = HelpWindow((700, 500), (50, 50),
                                 game_over_window, pygame.SRCALPHA)
        info_window = InfoWindow((160, 600), (50, 50), help_window)
        progress_bar = ProgressBar((640, 120), (640, 0), info_window)
        game_surface = GameSurface((640, 480), (0, 480),
                                   progress_bar, pygame.SRCALPHA)

        return game_surface

    def iterate(self):
        self.iteration += self.__ITERATION_CHANGE

    def increase_size(self):
        if self.size < self.__DEFAULT_SIZE:
            self.size += self.__SIZE_CHANGE

    def decrease_size(self):
        if self.size > self.__MIN_SIZE:
            self.size -= self.__SIZE_CHANGE

    def redraw(self):
        self.engine.add_size(self.size)
        self.drawer.connect_engine(self.engine)
        self.engine.redraw_objects()
        self.engine.redraw_surface()
        self.hero.sprite.redraw(self.size)
        self.engine.service.service_init(False)
