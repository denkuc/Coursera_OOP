from enum import Enum

import pygame
import collections


class Colors(Enum):
    BLACK = (0, 0, 0, 255)
    WHITE = (255, 255, 255, 255)
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    WOODEN = (153, 92, 0, 255)
    TEXT_COLOR = (128, 128, 255)


class ScreenHandle(pygame.Surface):
    TEXT_SIZE = 0

    def __init__(self, size: tuple, next_coord: tuple = None,
                 successor=None, *args):
        self.size = size
        self.next_coord = next_coord
        self.successor = successor

        super().__init__(self.size, *args)
        self.fill(Colors.WOODEN.value)
        self.game_engine = None

    def draw(self, game_display):
        if self.successor is not None:
            game_display.blit(self.successor, self.next_coord)
            self.successor.draw(game_display)

    def connect_engine(self, engine):
        if self.successor is not None:
            self.game_engine = engine
            self.successor.connect_engine(engine)

    @classmethod
    def __render(cls, text):
        font = pygame.font.SysFont("comicsansms", cls.TEXT_SIZE)
        return font.render(text, True, Colors.BLACK.value)

    def _blit_text(self, text, coords):
        return self.blit(self.__render(text), coords)


class GameSurface(ScreenHandle):
    def draw(self, game_display):
        self.draw_map()
        self.__draw_objects()
        self.draw_hero()
        super().draw(game_display)

    def draw_map(self):
        min_x, min_y = self.__calc_min_x_y()
        sprite_size = self.game_engine.sprite_size
        if self.game_engine.map:
            for i in range(len(self.game_engine.map[0]) - min_x):
                for j in range(len(self.game_engine.map) - min_y):
                    surface = self.game_engine.map[min_y+j][min_x+i].surface

                    self.blit(surface, (i*sprite_size, j*sprite_size))
        else:
            self.fill(Colors.WHITE.value)

    def __draw_objects(self):
        for obj in self.game_engine.objects:
            self.draw_object(obj.sprite.surface, obj.position)

    def draw_hero(self):
        hero = self.game_engine.hero
        self.draw_object(hero.sprite.surface, hero.position)

    def draw_object(self, surface, coord):
        size = self.game_engine.sprite_size
        min_x, min_y = self.__calc_min_x_y()

        self.blit(surface, ((coord[0] - min_x) * size,
                            (coord[1] - min_y) * size))

    def __calc_min_x_y(self):
        max_x, max_y = len(self.game_engine.map[1]), len(self.game_engine.map)
        sprite_size = self.game_engine.sprite_size
        hero_position = self.game_engine.hero.position
        min_x = (hero_position[0]*sprite_size
                 - self.size[0]//2) // sprite_size + 1
        min_y = (hero_position[1]*sprite_size
                 - self.size[1]//2) // sprite_size + 1
        if min_x < 0:
            min_x = 0
        elif (min_x*sprite_size + self.size[0]) > (max_x*sprite_size):
            min_x = (max_x*sprite_size - self.size[0]) // sprite_size
        if min_y < 0:
            min_y = 0
        elif (min_y*sprite_size + self.size[1]) > (max_y*sprite_size):
            min_y = (max_y*sprite_size - self.size[1]) // sprite_size

        return min_x, min_y


class ProgressBar(ScreenHandle):
    TEXT_SIZE = 20

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fill(Colors.WOODEN.value)

    def draw(self, game_display):
        self.fill(Colors.WOODEN.value)
        hero = self.game_engine.hero

        pygame.draw.rect(self, Colors.BLACK.value, (50, 30, 200, 30), 2)
        pygame.draw.rect(self, Colors.BLACK.value, (50, 70, 200, 30), 2)

        pygame.draw.rect(
            self, Colors.RED.value,
            (50, 30, 200 * hero.hp / hero.max_hp, 30)
        )
        if hero.exp < hero.exp_to_level_up:
            exp_to_draw = hero.exp
        else:
            exp_to_draw = hero.exp_to_level_up
        pygame.draw.rect(
            self, Colors.GREEN.value,
            (50, 70, 200 * exp_to_draw / hero.exp_to_level_up, 30)
        )

        self._blit_text(f'Hero at {hero.position}', (250, 0))

        self._blit_text(f'{self.game_engine.level} floor', (10, 0))

        self._blit_text(f'HP', (10, 30))
        self._blit_text(f'Exp', (10, 70))

        self._blit_text(f'{hero.hp}/{hero.max_hp}', (60, 30))

        self._blit_text(f'{hero.exp}/{hero.exp_to_level_up}',
                        (60, 70))

        self._blit_text(f'Level', (300, 30))
        self._blit_text(f'Gold', (300, 70))

        self._blit_text(f'{hero.level}', (360, 30))
        self._blit_text(f'{hero.gold}', (360, 70))

        self._blit_text(f'Str', (420, 30))
        self._blit_text(f'Luck', (420, 70))

        self._blit_text(f'{hero.stats["strength"]}', (480, 30))
        self._blit_text(f'{hero.stats["luck"]}', (480, 70))

        self._blit_text(f'SCORE', (550, 30))
        self._blit_text(f'{self.game_engine.score:.4f}', (550, 70))

        super().draw(game_display)
    # DONE draw next surface in chain


class InfoWindow(ScreenHandle):
    TEXT_SIZE = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 20
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        self.data.append(f"> {str(value)}")

    def draw(self, game_display):
        self.fill(Colors.WOODEN.value)
        for i, text in enumerate(self.data):
            self._blit_text(text, (5, 20 + 18 * i))

        super().draw(game_display)

    def connect_engine(self, engine):
        engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])

    def draw(self, game_display):
        alpha = 0
        if self.game_engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.game_engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True,
                              [(0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True,
                                       Colors.TEXT_COLOR.value),
                          (50, 50 + 30 * i))

                self.blit(font2.render(text[1], True,
                                       Colors.TEXT_COLOR.value),
                          (150, 50 + 30 * i))

        super().draw(game_display)


class GameOverWindow(ScreenHandle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, game_display):
        alpha = 0
        if self.game_engine.game_over:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("serif", 70, bold=True)
        font2 = pygame.font.SysFont("courier", 24)
        if self.game_engine.game_over:
            self.blit(font1.render("GAME OVER", True, Colors.RED.value),
                      (150, 200))
            self.blit(font2.render("Press Enter to restart",
                                   True, Colors.TEXT_COLOR.value),
                      (210, 270))

        super().draw(game_display)
