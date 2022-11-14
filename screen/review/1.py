import pygame
import random


class Vec2d:
    def __init__(self, x=1.0, y=1.0):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, other):
        return Vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vec2d):
            return self.x * other.x + self.y * other.y
        else:
            return Vec2d(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __len__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def int_pair(self):
        return int(self.x), int(self.y)


class Polyline:
    def __init__(self, points=(), speeds=()):
        self.points = [Vec2d(point) for point in points]
        self.speeds = [Vec2d(speed) for speed in speeds]
        self.p_count = len(self.points)
        self.knots_count = 1
        self.knots = []     # Так как Knot наследуется от Polyline, то он тоже будет содержать knots.
                            # Необходим другой контейнер для knots

    def add_point(self, new_point):
        self.points.append(Vec2d(x=new_point[0], y=new_point[1]))
        self.p_count += 1

    def add_speed(self):
        new_speed = [random.random() * 10, random.random() * 10]  # не уверен, если можно было изменять значение рандома
        self.speeds.append(Vec2d(x=new_speed[0], y=new_speed[1]))
# лишняя строка

    def set_points(self):
        for i in range(self.p_count):
            self.points[i] = self.points[i] + self.speeds[i]
            if not 0 <= self.points[i].x <= SCREEN_DIM[0]:
                self.speeds[i].x = -self.speeds[i].x
            if not 0 <= self.points[i].y <= SCREEN_DIM[1]:
                self.speeds[i].y = -self.speeds[i].y

    def draw_lines(self, width=3, color=(255, 255, 255)):
        if self.p_count >= 3:
            for i in range(-1, len(self.knots) - 1):
                pygame.draw.line(gameDisplay, color, self.knots[i].int_pair(),
                             self.knots[i + 1].int_pair(), width)  # codestyle: self должно начинаться там же, где и gameDisplay

    def draw_points(self, width=3, color=(255, 255, 255)):
        for point in self.points:
            pygame.draw.circle(gameDisplay, color, point.int_pair(), width)


class Knot(Polyline):
    def increase_knots(self):
        self.knots_count += 1 if self.knots_count < 30 else 0

    def decrease_knots(self):
        self.knots_count -= 1 if self.knots_count > 1 else 0

    def get_point(self, base_p, alpha):
        knot = (alpha * base_p[2] +
                (1 - alpha) * (alpha * base_p[1] + (1 - alpha) * base_p[0]))
        return knot

    def get_points(self, base_p):
        alpha = 1 / self.knots_count
        knots = [self.get_point(base_p, i * alpha) for i in range(self.knots_count)]
        return knots

    def get_knot(self):
        if self.p_count >= 3:
            self.knots.clear()
            for i in range(-2, self.p_count - 2):
                ptn = []
                ptn.append((self.points[i] + self.points[i + 1]) * 0.5)
                ptn.append(self.points[i + 1])
                ptn.append((self.points[i + 1] + self.points[i + 2]) * 0.5)
                self.knots.extend(self.get_points(ptn))


# лишние строки

SCREEN_DIM = (800, 600)

if __name__ == "__main__":
    fps = 60
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption(f"Indraw, speedrate - {int(fps / 2)} %, knots count - 1")
    gameDisplay.fill((0, 0, 0))

    pol = Knot()
    coloring = True
    filling = True
    working = True
    show_help = True
    pause = True

    hue = 0
    color = pygame.Color(0)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    gameDisplay.fill((0, 0, 0))
                    show_help = not show_help
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    pol.points, pol.speeds, pol.p_count = [], [], 0  # распаковка кортежа немного усложняет чтение
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    pol.increase_knots()
                    pygame.display.set_caption(f"Indraw, speedrate - {int(fps / 2)} %, knots count - {pol.knots_count}")
                    # повторяющееся действие, можно вынести в отдельную функцию или класс
                if event.key == pygame.K_KP_MINUS:
                    pol.decrease_knots()
                    pygame.display.set_caption(f"Indraw, speedrate - {int(fps / 2)} %, knots count - {pol.knots_count}")
                if event.key == pygame.K_UP:
                    fps += 20 if fps < 200 else 0
                    pygame.display.set_caption(f"Indraw, speedrate - {int(fps / 2)} %, knots count - {pol.knots_count}")
                if event.key == pygame.K_DOWN:
                    fps -= 20 if fps > 20 else 0
                    pygame.display.set_caption(f"Indraw, speedrate - {int(fps / 2)} %, knots count - {pol.knots_count}")
                if event.key == pygame.K_c:
                    coloring = not coloring
                if event.key == pygame.K_f:
                    filling = not filling

            if event.type == pygame.MOUSEBUTTONDOWN:
                pol.add_point(event.pos)
                pol.add_speed()

        gameDisplay.fill((0, 0, 0)) if filling else None
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)

        pol.draw_points()
        pol.get_knot()
        pol.draw_lines(color=color) if coloring else pol.draw_lines()

        pol.set_points() if not pause else None

        pygame.display.flip()
        pygame.time.Clock().tick(fps)
    pygame.display.quit()
    pygame.quit()
    exit(0)

