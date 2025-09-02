from numpy.random import randint

import Triangle
import Point2D
import random
import pygame
import math
import Coconut

class PalmV2():
    def __init__(self, position):
        self.position = position # left bottom corner
        self.all_triangles = []
        self.seed = random.randint(0,10000)
        self.top_trunk_color = (238, 214, 175)
        self.bottom_trunk_color = (205, 133, 63)
        self.top_leaves_color = (144, 238, 144)
        self.bottom_leaves_color = (34, 139, 34)
        self.max_height = 300
        self.bottom_width = 40
        self.nb_tree_parts = 6
        self.bottom_height = self.max_height/self.nb_tree_parts
        self.angle = math.radians(5) # mettre entre + ou - 5
        self.width_factor = 2
        self.last_c = Point2D.Point2D(0,0)
        self.last_d = Point2D.Point2D(0,0)

        self.nb_leaves = 10
        self.leaves_base_angle = 120
        self.leaves_start_angle = math.radians(180 + (180-self.leaves_base_angle)/2) # from right
        self.leaves_triangles_size = 25
        self.last_leaves_point = Point2D.Point2D(0,0)
        self.nb_triangles_by_leaves = 15
        self.triangle_leaves_rotation = math.radians(90/(self.nb_triangles_by_leaves - 1))

        self.coconuts = []
    def generate(self, window):
        random.seed(self.seed)
        self.angle = math.radians(random.randint(-5, 5))


        for i in range(self.nb_tree_parts):
            if i != 0:
                dx = math.tan(self.angle * i) * self.bottom_height * i

                a = self.last_c  # Coin en bas a gauche
                b = self.last_d # coin en bas a droite
                c = Point2D.Point2D(self.position.x + i * self.width_factor - dx, self.position.y - (i + 1) * self.bottom_height) # coin en haut a gauche
                d = Point2D.Point2D(self.position.x - i * self.width_factor + self.bottom_width - dx, self.position.y - (i + 1) * self.bottom_height) # coin en haut a droite

                self.last_c = c
                self.last_d = d

                tri = Triangle.Triangle(a, b, c, (0, 0, 0))
                self.all_triangles.append(tri)
                tri = Triangle.Triangle(d, c, b, (0, 0, 0))
                self.all_triangles.append(tri)
                if (i == self.nb_tree_parts - 1):
                    size = randint(10, 20)
                    c1 = Coconut.Coconut((self.last_c.x, self.last_c.y), size)
                    c1.generate()
                    self.coconuts.append(c1)
            else:
                a = Point2D.Point2D(self.position.x + i * self.width_factor, self.position.y - i * self.bottom_height)  # Coin en bas a gauche
                b = Point2D.Point2D(self.position.x - i * self.width_factor + self.bottom_width, self.position.y - i * self.bottom_height)  # coin en bas a droite
                c = Point2D.Point2D(self.position.x + i * self.width_factor, self.position.y - (i + 1) * self.bottom_height)  # coin en haut a gauche
                d = Point2D.Point2D(self.position.x - i * self.width_factor + self.bottom_width, self.position.y - (i + 1) * self.bottom_height)  # coin en haut a droite

                self.last_c = c
                self.last_d = d

                tri = Triangle.Triangle(a,b,c,(0,0,0))
                self.all_triangles.append(tri)
                tri = Triangle.Triangle(d,c,b,(0,0,0))
                self.all_triangles.append(tri)




        for tri in self.all_triangles:
            self.color_for_trunk(tri)

        for i in range(self.nb_leaves):
            pos_x = self.last_c.x + ((self.last_d.x - self.last_c.x) / (self.nb_leaves - 1)) * i
            p = Point2D.Point2D(pos_x, self.last_c.y)

            angle_increment = self.leaves_base_angle / (self.nb_leaves-1)
            angle = math.radians(angle_increment) * i + self.leaves_start_angle

            tri = Triangle.get_triangle_from_center(p, angle, self.leaves_triangles_size)
            self.color_for_leaves(tri, 0)
            self.last_leaves_point = tri.a

            self.all_triangles.append(tri)

            if self.nb_triangles_by_leaves > 1:
                if pos_x < self.last_c.x + (self.last_d.x - self.last_c.x)/2:
                    for j in range(self.nb_triangles_by_leaves - 1):
                        p = self.last_leaves_point

                        angle = math.radians(angle_increment) * i + self.leaves_start_angle - self.triangle_leaves_rotation * j

                        tri = Triangle.get_triangle_from_center(p, angle, self.leaves_triangles_size)
                        self.color_for_leaves(tri, j + 1)

                        self.last_leaves_point = tri.a

                        self.all_triangles.append(tri)
                else:
                    for j in range(self.nb_triangles_by_leaves - 1):
                        p = self.last_leaves_point

                        angle = math.radians(angle_increment) * i + self.leaves_start_angle + self.triangle_leaves_rotation * j

                        tri = Triangle.get_triangle_from_center(p, angle, self.leaves_triangles_size)
                        self.color_for_leaves(tri, j + 1)

                        self.last_leaves_point = tri.a

                        self.all_triangles.append(tri)

    def color_for_trunk(self, triangle):
        altitude = triangle.a.y

        y_max = self.position.y
        y_min = self.max_height

        t = (altitude - y_min)/(y_max - y_min)

        triangle.color = self.linear_interpolation_color(self.bottom_trunk_color,self.top_trunk_color, t)

    def color_for_leaves(self, triangle, i):
        altitude = i

        y_max = self.nb_triangles_by_leaves
        y_min = 0

        t = (altitude - y_min)/(y_max - y_min)

        triangle.color = self.linear_interpolation_color(self.bottom_leaves_color,self.top_leaves_color, t)

    def linear_interpolation_color(self,color1, color2, factor):
        color = (int(color1[0] + (color2[0] - color1[0])*factor),
                 int(color1[1] + (color2[1] - color1[1])*factor),
                 int(color1[2] + (color2[2] - color1[2])*factor))

        return color

    def update(self, bpm):
        print("TODO")

    def manage_sun(self, window, time):
        for tri in self.all_triangles:
            pygame.draw.polygon(window, tri.color, tri.to_pygame_point())
        for c in self.coconuts:
            c.draw(window)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    test = PalmV2(Point2D.Point2D(screen.get_width()/2, screen.get_height()/2))
    test.generate(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks() / 1000.0

        screen.fill((255, 255, 255))
        test.manage_sun(screen, current_time)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()