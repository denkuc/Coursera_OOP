#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import random


class Vec2d:
    """Класс вектора"""
    def __init__(self, pos=(0, 0)):
        self.x = pos[0]
        self.y = pos[1]

    def __add__(self, other):
        return Vec2d((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return Vec2d((self.x - other.x, self.y - other.y))

    def __mul__(self, other):
        return Vec2d((self.x * other, self.y * other))

    def __len__(self):
        return (self.x**2 + self.y**2)**(1/2)

    def int_pair(self):
        return int(self.x), int(self.y)


class Polyline:
    """Класс ломаной кривой"""
    width = 3

    def __init__(self, display, color=(255, 255, 255), screen_dim=(800, 600)):
        self.points = []
        self.speeds = []
        self.display = display
        self.color = color
        self.screen_dim = screen_dim

    def add_point(self, p, s):
        """Добавляет точку кривой"""
        self.points.append(Vec2d(p))
        self.speeds.append(Vec2d(s))

    def remove_point(self):
        """Удаляет последнюю точку кривой"""
        if len(self.points) == len(self.speeds) and len(self.points) > 0:
            self.points.pop()
            self.speeds.pop()

    def clear(self):
        """Удаляет все точки кривой"""
        self.points.clear()
        self.speeds.clear()

    def increase_speed(self):
        """Увеличивает скорость движения точек кривой"""
        self.speeds = list(map(lambda s: s*1.5, self.speeds))

    def decrease_speed(self):
        """Уменьшает скорость движения точек кривой"""
        self.speeds = list(map(lambda s: s*(1/1.5), self.speeds))

    def set_points(self):
        """функция перерасчета координат опорных точек"""
        for p in range(len(self.points)):
            self.points[p] = self.points[p] + self.speeds[p]
            if self.points[p].x > self.screen_dim[0] or self.points[p].x < 0:
                self.speeds[p] = Vec2d((- self.speeds[p].x, self.speeds[p].y))
            if self.points[p].y > self.screen_dim[1] or self.points[p].y < 0:
                self.speeds[p] = Vec2d((self.speeds[p].x, -self.speeds[p].y))

    def draw_points(self):
        """функция отрисовки точек на экране"""
        for p in self.points:
            pygame.draw.circle(display, self.color,
                               (p.int_pair()), Polyline.width)


class Knot(Polyline):
    """Клас сглаженной кривой"""
    steps = 35

    def __init__(self, display, color=(255, 255, 255), screen_dim=(800, 600)):
        super(Knot, self).__init__(display, color, screen_dim)
        self.hue = 0

    @classmethod
    def get_steps(self):
        """Возвращает количество точек для сглаживания"""
        return Knot.steps

    def get_knot(self):
        """Рассчитывае точки сглаженной кривой из узловых точек"""
        def get_point(points, alpha, deg=None):
            if deg is None:
                deg = len(points) - 1
            if deg == 0:
                return points[0]
            return (points[deg] * alpha) + (get_point(points, alpha, deg - 1) * (1 - alpha))

        def get_points(base_points, count):
            alpha = 1 / count
            res = []
            for i in range(count):
                res.append(get_point(base_points, i * alpha))
            return res

        if len(self.points) < 3:
            return []
        res = []
        for i in range(-2, len(self.points) - 2):
            ptn = []
            ptn.append(((self.points[i] + self.points[i + 1]) * 0.5))
            ptn.append(self.points[i + 1])
            ptn.append(((self.points[i + 1] + self.points[i + 2]) * 0.5))

            res.extend(get_points(ptn, Knot.steps))
        return res

    def draw_points(self):
        """функция отрисовки кривой на экране"""
        super(Knot, self).draw_points()
        color_ = pygame.Color(0)
        self.hue = (self.hue + 1) % 360
        color_.hsla = (self.hue, 100, 50, 100)
        ps = self.get_knot()
        for p_n in range(-1, len(ps) - 1):
            pygame.draw.line(display, color_,
                             (int(ps[p_n].x), int(ps[p_n].y)),
                             (int(ps[p_n + 1].x), int(ps[p_n + 1].y)), Knot.width)


def draw_help(display, steps):
    """функция отрисовки экрана справки программы"""
    display.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 22)
    font2 = pygame.font.SysFont("serif", 22)
    data = []
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["1", "Add new knot"])
    data.append(["2", "Remove last knot"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["PageUp", "Increase speed of last knot"])
    data.append(["PageDown", "Decrease speed of last knot"])
    data.append(["Ctrl + PageUp", "Increase speed of all knot"])
    data.append(["Ctrl + PageDown", "Decrease speed of all knot"])
    data.append(["Mouse left", "Add key point to last knot"])
    data.append(["Mouse right", "Remove key point from last knot"])
    data.append(["Ctrl + Mouse left", "Add key point to all knots"])
    data.append(["Ctrl + Mouse right", "Remove key point from all knots"])
    data.append(["", ""])
    data.append([str(steps), "Current points"])

    pygame.draw.lines(display, (255, 50, 50, 255), True, [
        (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        display.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 50 + 30 * i))
        display.blit(font2.render(
            text[1], True, (128, 128, 255)), (400, 50 + 30 * i))


def random_color():
    """Генерация случайного цвета"""
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def add_key_point(kn, p):
    s = (random.random() * 2, random.random() * 2)
    kn.add_point(p, s)


# =======================================================================================
# Основная программа
# =======================================================================================
if __name__ == "__main__":
    pygame.init()
    screen_dim = (800, 600)
    display = pygame.display.set_mode(screen_dim)
    pygame.display.set_caption('MyScreenSaver')

    working = True
    color = pygame.Color(255, 255, 255)
    knots = [Knot(display, color=color, screen_dim=screen_dim)]

    show_help = False
    pause = True

    while working:
        for event in pygame.event.get():
            mods = pygame.key.get_mods()
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    knots.clear()
                    knots.append(Knot(display))
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_1:
                    knots.append(Knot(display, color=random_color()))
                if event.key == pygame.K_2:
                    if len(knots) > 1:
                        knots.pop()
                if event.key == pygame.K_KP_PLUS:
                    Knot.steps += 1
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    Knot.steps -= 1 if Knot.steps > 1 else 0
                if event.key == pygame.K_PAGEUP:
                    knots[-1].increase_speed()
                if event.key == pygame.K_PAGEDOWN:
                    knots[-1].decrease_speed()
                if mods & pygame.KMOD_CTRL and event.key == pygame.K_PAGEUP:
                    for it in knots:
                        it.increase_speed()
                if mods & pygame.KMOD_CTRL and event.key == pygame.K_PAGEDOWN:
                    for it in knots:
                        it.decrease_speed()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mods & pygame.KMOD_CTRL and event.button == 1:
                    for it in knots:
                        add_key_point(it, event.pos)
                elif mods & pygame.KMOD_CTRL and event.button == 3:
                    for it in knots:
                        it.remove_point()
                elif event.button == 1:
                    add_key_point(knots[-1], event.pos)
                elif event.button == 3:
                    knots[-1].remove_point()

        display.fill((0, 0, 0))
        for kn in knots:
            kn.draw_points()
            if not pause:
                kn.set_points()
        if show_help:
            draw_help(display, Knot.get_steps())

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)
