import math
import random
from collections import OrderedDict
from typing import Iterator

import pygame


class Vec2d:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def int_pair(self):
        return int(self.x), int(self.y)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, y):
        self.__y = y

    def __add__(self, other: 'Vec2d') -> 'Vec2d':
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vec2d') -> 'Vec2d':
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, multiplier) -> 'Vec2d':
        return Vec2d(self.x * multiplier, self.y * multiplier)

    def __len__(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def __eq__(self, other: 'Vec2d'):
        return self.x == other.x and self.y == other.y

    def is_x_out_of_range(self):
        return self.x > screen_dimension.x or self.x < 0

    def is_y_out_of_range(self):
        return self.y > screen_dimension.y or self.y < 0


screen_dimension = Vec2d(800, 600)


class MovingPoint:
    def __init__(self, coords: tuple):
        self.coords = Vec2d(coords[0], coords[1])
        self.speed = Vec2d()

    def set_speed(self):
        self.speed.x = self.__get_random_value()
        self.speed.y = self.__get_random_value()

    @staticmethod
    def __get_random_value():
        return random.random() * 2

    def change_speed(self, value):
        self.speed = self.speed * value


class Collection:
    def __init__(self):
        self.__elements = []

    def __iter__(self):
        return iter(self.__elements)

    def __next__(self):
        element = next(self.__elements) or None
        if element is None:
            raise StopIteration

        return element

    def __getitem__(self, key):
        return self.__elements[key]

    def __len__(self):
        return len(self.__elements)

    def add(self, element):
        self.__elements.append(element)

    def clear(self):
        self.__elements = []

    def drop_last(self):
        self.__elements.pop()


class MovingPointCollection(Collection):
    def __iter__(self) -> Iterator[MovingPoint]:
        return super().__iter__()

    def add(self, element: MovingPoint):
        super().add(element)

    def get_next_point(self, index) -> MovingPoint:
        if index == len(self):
            return self[1]
        elif index == len(self) - 1:
            return self[0]
        else:
            return self[index + 1]

    def change_speed(self, value):
        [point.change_speed(value) for point in self]


class Polyline:
    def __init__(self, drawer: 'GameDisplayDrawer'):
        self.moving_points = MovingPointCollection()
        self._drawer = drawer

    @property
    def moving_points(self) -> MovingPointCollection:
        return self.__moving_points

    @moving_points.setter
    def moving_points(self, moving_points: MovingPointCollection):
        self.__moving_points = moving_points

    def add_moving_point(self, moving_point: MovingPoint):
        self.moving_points.add(moving_point)

    def set_points(self):
        new_moving_points = MovingPointCollection()
        for moving_point in self.moving_points:
            moving_point.coords = moving_point.coords + moving_point.speed
            if moving_point.coords.is_x_out_of_range():
                moving_point.speed.x = -moving_point.speed.x
            if moving_point.coords.is_y_out_of_range():
                moving_point.speed.y = -moving_point.speed.y

            new_moving_points.add(moving_point)

        self.moving_points = new_moving_points

    def draw_points(self):
        for moving_point in self.moving_points:
            self._drawer.draw_default_circle(moving_point.coords)


class SmoothieMaker:
    def __init__(self, count):
        self.count = count

    def get_smoothing_points(self, first_point, second_point, third_point):
        smoothing_base = [(first_point + second_point) * 0.5,
                          second_point,
                          (second_point + third_point) * 0.5]

        return self.__get_smoothing_points_from_base(smoothing_base)

    def __get_smoothing_points_from_base(self, base_points):
        alpha = 1 / self.count
        res = [self.__get_point(base_points, i * alpha)
               for i in range(self.count)]
        return res

    def __get_point(self, base, alpha, deg=None):
        if deg is None:
            deg = len(base) - 1
        if deg == 0:
            return base[0]

        first_vector = base[deg] * alpha
        second_vector = self.__get_point(base, alpha, deg - 1) * (1 - alpha)
        return first_vector + second_vector


class Knot(Polyline):
    __MIN_POINTS_COUNT = 3

    def __init__(self, drawer: 'GameDisplayDrawer', polyline: Polyline):
        super().__init__(drawer)
        self.__smoothie_maker = SmoothieMaker(self._drawer.get_steps())

        if len(polyline.moving_points) < self.__MIN_POINTS_COUNT:
            self.moving_points.clear()
        else:
            self.moving_points = self.__get_knot_points(polyline)

    def __get_knot_points(self, polyline):
        knot_moving_points = MovingPointCollection()
        polyline_moving_points = polyline.moving_points

        for index, point in enumerate(polyline_moving_points):
            next_point = polyline_moving_points.get_next_point(index)
            one_after_point = polyline_moving_points.get_next_point(index+1)

            smoothing_points = self.__smoothie_maker.get_smoothing_points(
                point.coords, next_point.coords, one_after_point.coords
            )

            for smoothing_point in smoothing_points:
                knot_moving_point = MovingPoint(smoothing_point.int_pair())
                knot_moving_points.add(knot_moving_point)

        return knot_moving_points

    def draw_line(self, color):
        for index, point in enumerate(self.moving_points):
            next_point = self.moving_points.get_next_point(index)

            self._drawer.draw_line(point.coords, next_point.coords, color)


class HelpDrawer:
    __HELP_BACKGROUND = (50, 50, 50)
    __COURIER_FONT = "courier"
    __SERIF_FONT = "serif"

    def __init__(self, display, get_steps, get_speed):
        self.__display = display
        self.__get_steps = get_steps
        self.__get_speed = get_speed

    def draw_help(self):
        self.__display.fill(self.__HELP_BACKGROUND)
        self.__draw_help_lines()
        self.__draw_blits()

    def __draw_help_lines(self):
        lines_color = (255, 50, 50, 255)
        lines_are_closed = True
        lines_coords = [(0, 0), (800, 0), (800, 600), (0, 600)]
        lines_width = 5
        pygame.draw.lines(self.__display, lines_color,
                          lines_are_closed, lines_coords, lines_width)

    def __draw_blits(self):
        steps = str(self.__get_steps())
        speed = str(round(self.__get_speed(), 5))
        help_map = OrderedDict({'F1': 'Show Help',
                                'R': 'Restart',
                                'P': 'Pause/Play',
                                'Num+': 'More smoothing points',
                                'Num-': 'Less smoothing points',
                                'PageUp': 'Increase speed',
                                'PageDown': 'Decrease speed',
                                'Backspace': 'Remove last point',
                                '': '',
                                steps: 'Current points',
                                speed: 'Current speed'})

        for row_index, (key, text) in enumerate(help_map.items()):
            self.__draw_one_blit(self.__COURIER_FONT, key, 100, row_index)
            self.__draw_one_blit(self.__SERIF_FONT, text, 300, row_index)

    def __draw_one_blit(self, font_name, text, text_x, row_index):
        font = self.__get_font(font_name)
        antialias = True
        text_color = (128, 128, 255)
        text_coords = (text_x, 100 + 30 * row_index)
        self.__display.blit(font.render(text, antialias, text_color),
                            text_coords)

    @staticmethod
    def __get_font(font_name):
        return pygame.font.SysFont(font_name, 24)


class GameDisplayDrawer:
    __DEFAULT_CIRCLE_COLOR = (255, 255, 255)
    __GAME_BACKGROUND = (0, 0, 0)
    __CIRCLE_WIDTH = 3
    __LINE_WIDTH = 3

    def __init__(self, game: 'Game'):
        self.__game = game
        self.__display = pygame.display.set_mode(screen_dimension.int_pair())
        self.__help_drawer = HelpDrawer(self.__display,
                                        self.get_steps,
                                        self.get_speed)

    def get_steps(self):
        return self.__game.steps

    def get_speed(self):
        return self.__game.speed_value

    def draw_line(self, first_coords: Vec2d, second_coords: Vec2d, color):
        pygame.draw.line(self.__display,
                         color,
                         first_coords.int_pair(),
                         second_coords.int_pair(),
                         self.__LINE_WIDTH)

    def draw_default_circle(self, coords: Vec2d):
        pygame.draw.circle(self.__display,
                           self.__DEFAULT_CIRCLE_COLOR,
                           coords.int_pair(),
                           self.__CIRCLE_WIDTH)

    def fill_game_background(self):
        self.__display.fill(self.__GAME_BACKGROUND)

    def draw_help(self):
        self.__help_drawer.draw_help()


class LineColor:
    def __init__(self):
        self.__hue = 0
        self.color = pygame.Color(0)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, color):
        self.__color = color

    def change_color(self):
        self.__hue = (self.__hue + 1) % 360
        self.color.hsla = (self.__hue, 100, 50, 100)


class Game:
    __SPEED_UP_CHANGE = 1.05
    __SPEED_DOWN_CHANGE = 0.95

    def __init__(self):
        self.steps = 35
        self.speed_value = 1
        self.working = True
        self.show_help = False
        self.pause = True

    def speed_up(self):
        self.speed_value *= self.__SPEED_UP_CHANGE

    def speed_down(self):
        self.speed_value *= self.__SPEED_DOWN_CHANGE


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game_drawer = GameDisplayDrawer(game)
    pygame.display.set_caption("MyScreenSaver")

    game_polyline = Polyline(game_drawer)
    line_color = LineColor()

    while game.working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.working = False
                if event.key == pygame.K_r:
                    game_polyline = Polyline(game_drawer)
                    game.speed_value = 0
                if event.key == pygame.K_p:
                    game.pause = not game.pause
                if event.key == pygame.K_KP_PLUS:
                    game.steps += 1
                if event.key == pygame.K_F1:
                    game.show_help = not game.show_help
                if event.key == pygame.K_KP_MINUS:
                    game.steps -= 1 if game.steps > 1 else 0
                if event.key == pygame.K_BACKSPACE:
                    game_polyline.moving_points.drop_last()
                if event.key == pygame.K_PAGEUP:
                    game.speed_up()
                    game_polyline.moving_points.change_speed(game.speed_value)
                if event.key == pygame.K_PAGEDOWN:
                    game.speed_down()
                    game_polyline.moving_points.change_speed(game.speed_value)

            if event.type == pygame.MOUSEBUTTONDOWN:
                new_point = MovingPoint(event.pos)
                new_point.set_speed()
                game_polyline.add_moving_point(new_point)

        game_drawer.fill_game_background()
        line_color.change_color()

        game_polyline.draw_points()
        game_knot = Knot(game_drawer, game_polyline)
        game_knot.draw_line(line_color.color)

        if not game.pause:
            game_polyline.set_points()
        if game.show_help:
            game_drawer.draw_help()

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
