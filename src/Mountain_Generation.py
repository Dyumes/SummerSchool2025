import random
import pygame
import math

from sympy.benchmarks.bench_meijerint import normal

import Triangle
import Point2D
import pyautogui
from Generation import normalScreenSize

class MountainV2:
    def __init__(self):
        self.max_height = 2000/normalScreenSize * pyautogui.size()[0]
        self.animation_max_height = 1000/normalScreenSize * pyautogui.size()[0]
        self.height = self.max_height
        self.real_height = self.max_height
        self.width = 500
        self.nb_subdivision = 3
        self.pos_x = 50 # position x au coin en bas a gauche
        self.floor_position = 600/normalScreenSize * pyautogui.size()[0]
        self.seed = random.randint(0, 10000)
        self.all_triangles = []
        self.nb_layers = 5
        self.snow_height_trigger = 0.75 * self.max_height
        self.rock_height_trigger = 0.4 * self.max_height
        self.grass_color = 	(0,18,255)
        self.rock_color = (70,83,255)
        self.snow_color = 	(239,240,255)
        self.animation_time = 1
        self.start_time = 0
        self.can_move = False

    def midpoint_displacement(self, start, end, max_height, nb_subdivision, result):
        if nb_subdivision == 0:
            result.append(start)
            return

        middle_x = (start.x + end.x)/2
        middle_y = (start.y + end.y)/2

        disp = max_height * (0.5 ** nb_subdivision)
        y_offset = random.uniform(-disp, disp)

        middle_y = middle_y + y_offset
        middle_y = max(self.floor_position - max_height, min(self.floor_position - 0.2 * max_height, middle_y))

        mid = Point2D.Point2D(middle_x,middle_y)

        self.midpoint_displacement(start,mid, max_height/2, nb_subdivision - 1, result)
        self.midpoint_displacement(mid,end, max_height/2, nb_subdivision - 1, result)

    def createTriangle(self, points, floor_y, nb_layers):
        columns = []

        for p in points:
            column = []
            for i in range(nb_layers + 1):
                interpolation_factor = i / nb_layers
                x = p.x
                y = floor_y - (floor_y - p.y) * interpolation_factor
                column.append(Point2D.Point2D(x,y))
            columns.append(column)

        triangles = []
        for i in range(len(columns) - 1):
            first_column = columns[i]
            next_column = columns[i + 1]

            for j in range(nb_layers):
                a = first_column[j]
                b = first_column[j + 1]
                c = next_column[j]
                d = next_column[j + 1]

                color = self.color_for_triangle(Triangle.Triangle(a, c, b, None))
                triangles.append(Triangle.Triangle(a, c, b, color))

                color = self.color_for_triangle(Triangle.Triangle(b, c, d, None))
                triangles.append(Triangle.Triangle(b, c, d, color))
        self.all_triangles = triangles

    def generate(self):
        random.seed(self.seed)
        res = []
        self.midpoint_displacement(Point2D.Point2D(self.pos_x,self.floor_position),Point2D.Point2D(self.pos_x + self.width,self.floor_position),self.max_height,self.nb_subdivision, res)
        res.append(Point2D.Point2D(self.pos_x + self.width, self.floor_position))

        max_altitude = self.floor_position - res[0].y
        for p in res:
            if self.floor_position - p.y > max_altitude:
                max_altitude = self.floor_position - p.y

        self.snow_height_trigger = 0.8 * max_altitude
        self.rock_height_trigger = 0.4 * max_altitude

        self.createTriangle(res,self.floor_position,self.nb_layers)

    def linear_interpolation_color(self,color1, color2, factor):
        color = (int(color1[0] + (color2[0] - color1[0])*factor),
                 int(color1[1] + (color2[1] - color1[1])*factor),
                 int(color1[2] + (color2[2] - color1[2])*factor))

        return color

    def color_for_triangle(self, triangle):
        altitude_a = self.floor_position - triangle.a.y
        altitude_b = self.floor_position - triangle.b.y
        altitude_c = self.floor_position - triangle.c.y

        moy = (altitude_a + altitude_b + altitude_c) / 3.0

        if moy >= self.snow_height_trigger:
            return self.snow_color
        elif moy >= self.rock_height_trigger:
            t = (moy - self.rock_height_trigger) / (self.snow_height_trigger - self.rock_height_trigger)
            return self.linear_interpolation_color(self.rock_color, self.snow_color, t)
        else:
            t = moy / self.rock_height_trigger
            return self.linear_interpolation_color(self.grass_color, self.rock_color, t)

    def update(self, time):
        animation_current_time = time - self.start_time

        if self.can_move:
            if animation_current_time >= self.animation_time:
                self.height = 0 + self.max_height
            elif  animation_current_time < 0.2 * self.animation_time:
                self.height = self.max_height + self.animation_max_height / (0.2 * self.animation_time) * animation_current_time
            elif animation_current_time > 0.6 * self.animation_time:
                self.height = self.max_height + self.animation_max_height / (0.6 * self.animation_time - self.animation_time) * animation_current_time + (self.animation_max_height / 0.4)
            else:
                self.height = self.max_height + self.animation_max_height * 0.1 * math.sin(animation_current_time * 20) + self.animation_max_height

    def manage_mountain(self, screen, time):
        self.update(time)
        for tri in self.all_triangles:
            scale = self.height / self.real_height
            p1 = (tri.a.x, self.floor_position - (self.floor_position - tri.a.y) * scale)
            p2 = (tri.b.x, self.floor_position - (self.floor_position - tri.b.y) * scale)
            p3 = (tri.c.x, self.floor_position - (self.floor_position - tri.c.y) * scale)
            pygame.draw.polygon(screen, tri.color, [p1, p2, p3])

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()

    mountains = []
    for i in range(12):
        temp = MountainV2()
        temp.width = screen.get_width() / 12
        temp.pos_x = temp.width * i
        temp.generate()
        temp.real_height = temp.max_height
        mountains.append(temp)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks() / 1000.0

        screen.fill((255, 255, 255))
        for e in mountains:
            e.manage_mountain(screen, current_time)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()