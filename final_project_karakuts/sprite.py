import os
from abc import ABC
from random import randint

import pygame

from objects import MagicObject, Ally, Enemy, Hero


class BaseSprite(ABC):
    TEXTURE = "texture"
    SPRITE_MEMO = {}

    def __init__(self, icon):
        self.icon = icon
        self.surface = None

    def redraw(self, size):
        cached_surface = self.__get_cached(size)
        if cached_surface is not None:
            self.surface = cached_surface
        else:
            sprite_square = (size, size)
            icon = pygame.image.load(self.icon).convert_alpha()
            icon = pygame.transform.scale(icon, sprite_square)
            self.surface = pygame.Surface(sprite_square, pygame.HWSURFACE)
            self.surface.blit(icon, (0, 0))
            self.SPRITE_MEMO[self.icon][size] = self.surface

    def __get_cached(self, size):
        icon_cache = self.SPRITE_MEMO.get(self.icon)
        if icon_cache:
            if icon_cache.get(size):
                return icon_cache.get(size)
        else:
            self.SPRITE_MEMO[self.icon] = {}


class WallSprite(BaseSprite):
    WALL_TEXTURE = os.path.join(BaseSprite.TEXTURE, "wall.png")

    def __init__(self):
        super().__init__(self.WALL_TEXTURE)


class FloorSprite(BaseSprite):
    GROUND_TEXTURE = os.path.join(BaseSprite.TEXTURE, "Ground_{}.png")

    def __init__(self):
        super().__init__(self.GROUND_TEXTURE.format(randint(1, 3)))


class MagicObjectSprite(BaseSprite):
    OBJECT_TEXTURE = os.path.join(BaseSprite.TEXTURE, "objects")

    def __init__(self, img_path):
        super().__init__(os.path.join(self.OBJECT_TEXTURE, img_path))


class AllySprite(BaseSprite):
    ALLY_TEXTURE = os.path.join(BaseSprite.TEXTURE, "ally")

    def __init__(self, img_path):
        super().__init__(os.path.join(self.ALLY_TEXTURE, img_path))


class EnemySprite(BaseSprite):
    ENEMY_TEXTURE = os.path.join(BaseSprite.TEXTURE, "enemies")

    def __init__(self, img_path):
        super().__init__(os.path.join(self.ENEMY_TEXTURE, img_path))


class HeroSprite(BaseSprite):
    HERO_TEXTURE = os.path.join(BaseSprite.TEXTURE, "Hero.png")

    def __init__(self):
        super().__init__(self.HERO_TEXTURE)


class SpriteFactory:
    @staticmethod
    def get_sprite_for_wall():
        return WallSprite()

    @staticmethod
    def get_sprite_for_floor():
        return FloorSprite()

    @staticmethod
    def get_sprite_for_object(instance):
        if isinstance(instance, Hero):
            return HeroSprite()
        elif isinstance(instance, MagicObject):
            return MagicObjectSprite(instance.sprite_icon_path)
        elif isinstance(instance, Ally):
            return AllySprite(instance.sprite_icon_path)
        elif isinstance(instance, Enemy):
            return EnemySprite(instance.sprite_icon_path)

        return None
