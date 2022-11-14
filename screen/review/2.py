import pygame
import random
import math
from abc import ABC, abstractmethod

SCREEN_DIM = (800, 600)


'''Class vectors[2]. Reload operators  add, sub, mul 
for operation with Vec2d.
'''
class Vec2d:

	def __init__(self, x, y):
		self.x = x
		self.y = y


	def __add__(self, vec):
		# Method add 2 vectors & return Vec2d
		return Vec2d(self.x + vec.x, self.y + vec.y)


	def __mul__(self, k):
		# Method mul vectors on k & return Vec2d
		return Vec2d(self.x * k, self.y * k)


	def __sub__(self, vec):
		# Method sub 2 vectors & return Vec2d
	    return Vec2d(self.x - vec.x, self.y - vec.y)


	def len(self) -> int:
		# Method return lenght Vec2d
	    return math.sqrt(self.x * self.x + self.y * self.y)


	def int_pair(self):
		# Method return X & Y coordinates -> tuple
		return self.x, self.y


class Polyline:

	def __init__(self, gameDisplay):
	    self.gameDisplay = gameDisplay
	    self.points = []
	    self.speeds = []
	    self.steps = 35
	    self.delay_c = 0
	    self.delay_max = 0


	def draw_points(self, style="points", width=3, color=(255, 255, 255)):
		# Method for drawing points or lines on screen.
		points = self.get_knot()
		if style == "line":
			for p_n in range(-1, len(points) - 1):
				'''add lines to screen. start&end&width'''
				pygame.draw.line(self.gameDisplay, color,
								(int(points[p_n].x), int(points[p_n].y)),
								(int(points[p_n + 1].x), int(points[p_n + 1].y)), width)

		elif style == "points":
			for p in self.points:
				'''add points to screen. center & radiius'''
				pygame.draw.circle(self.gameDisplay, color,
	  							  (int(p.x), int(p.y)), width)


	def set_points(self):
		''' Method for recountin coordinates for all points
		of lines.
		'''
		self.delay_c += 1

		if(self.delay_c >= self.delay_max):
		    for p in range(len(self.points)):
		        self.points[p] = (self.points[p] + self.speeds[p])
		        if self.points[p].x > SCREEN_DIM[0] or self.points[p].x < 0:
		            self.speeds[p].x = -self.speeds[p].x
		        if self.points[p].y > SCREEN_DIM[1] or self.points[p].y < 0:
		            self.speeds[p].y = -self.speeds[p].y

		    self.delay_c = 0
		self.get_knot()


	def add_point(self, position):
		# Method for addition point to list of points for one line.
		self.points.append(position)
		rand = Vec2d(random.random()*2, random.random()*2)
		self.speeds.append(rand)
		self.get_knot()


	def delete_point(self):
		# Delete the last point in list
		if(len(self.points) > 0):
			self.points.pop()


	def slow_draw(self):
		# This method increment delay count. This allows draw slowly.
		self.delay_max += 1


	def fast_draw(self):
		# This method decrement delay count. This allows draw faster.
		if (self.delay_max >= 1):
			self.delay_max -= 1
		else:
			self.delay_max = 0

	@abstractmethod
	def get_knot(self):
		pass


class Knot(Polyline):

	def get_point(self, points, alpha, deg=None):
	    if deg is None:
	        deg = len(points) - 1
	    if deg == 0:
	        return points[0]
	    return ((points[deg]*alpha) + (self.get_point(points, alpha, deg - 1)*(1 - alpha)))


	def get_points(self, base_points):
	    alpha = 1 / self.steps
	    res = []
	    for i in range(self.steps):
	        res.append(self.get_point(base_points, i * alpha))
	    return res


	def get_knot(self):
		# Recounting compliment point in polyline
	    if len(self.points) < 3:
	        return []
	    res = []

	    for i in range(-2, len(self.points) - 2):
	        ptn = []
	        ptn.append((self.points[i] + self.points[i + 1]) * 0.5)
	        ptn.append(self.points[i + 1])
	        ptn.append((self.points[i + 1] + self.points[i + 2]) * 0.5)
	        res.extend(self.get_points(ptn))
	    return res


def draw_help(poly):
	# Drowing menu on screen
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 24)
    font2 = pygame.font.SysFont("serif", 24)
    data = []
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["D", "Delete point"])
    data.append(["S", "Slow speed draw"])
    data.append(["F", "Fast speed draw"])
    data.append(["A", "Add new knot"])
    data.append(["Z", "Decrement number active knot"])
    data.append(["X", "Increment number active knot"])
    data.append([str(poly_count + 1), "Active knot"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["", ""])
    data.append([str(poly.steps), "Current points"])

    pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
        (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    # init 1 Knot without points
    poly = []
    poly_count = 0
    poly.append(Knot(gameDisplay)) 

    working = True
    show_help = False
    pause = True

    hue = 0
    color = pygame.Color(0)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                	for i in range(len(poly)):
	                    poly = []	                    
	                    poly.append(Knot()) 
	                    poly_count = 0
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    poly[poly_count].steps += 1
                if event.key == pygame.K_F1:
                    show_help = not show_help
                if event.key == pygame.K_KP_MINUS:
                    poly[poly_count].steps -= 1 if poly[poly_count].steps > 1 else 0

                if event.key == pygame.K_d:
                	# delet the last point in active line
                    poly[poly_count].delete_point()  
                if event.key == pygame.K_s:
                	# draw slowly active line
                    poly[poly_count].slow_draw()  	 
                if event.key == pygame.K_f:
                	# draw faster active line
                    poly[poly_count].fast_draw()  	 
                if event.key == pygame.K_a:
                	# add new line & do one active
                    poly.append(Knot(gameDisplay))				
                    poly_count += 1 
                if event.key == pygame.K_z:
                	# change active line: -1
                    if(poly_count  != 0):
                    	poly_count -= 1
                    else:
                    	poly_count = 0
                if event.key == pygame.K_x:
                	# change active line: +1
                	if(poly_count != (len(poly) - 1)):
                		poly_count += 1
                	elif(poly_count >= (len(poly) - 1)):
                		poly_count = len(poly) - 1


            if event.type == pygame.MOUSEBUTTONDOWN:
                poly[poly_count].add_point(Vec2d(event.pos[0], event.pos[1]))                

        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)
        for i in range(len(poly)):
        	# draw all lines
	        poly[i].draw_points("points")
	        poly[i].draw_points("line", 3, color)
        if not pause:
        	for i in range(len(poly)):
        		# recounting all point in all lines
        		poly[i].set_points()
        if show_help:
        	draw_help(poly[poly_count])

        pygame.display.flip()

    pygame.display.quit()
    pygame.quit()
    exit(0)