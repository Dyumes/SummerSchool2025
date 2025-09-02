import pyautogui
from numpy.random import randint
import Triangle
import Point2D
import random
import pygame
import math
import Coconut
from src.Generation import normalScreenSize


class PalmV2():
    def __init__(self, position, depth = 1):
        self.depth = depth
        self.position = position # left bottom corner
        self.all_triangles = []
        self.original_points = []
        self.seed = random.randint(0,10000)
        self.top_trunk_color = (200, 0, 180)
        self.bottom_trunk_color = (50, 0, 50)
        self.top_leaves_color = (0, 255, 180)
        self.bottom_leaves_color = (0, 120, 80)
        self.max_height = 500 * self.depth /normalScreenSize * pyautogui.size()[0]
        self.bottom_width = 75 * self.depth /normalScreenSize * pyautogui.size()[0]
        self.nb_tree_parts = 6
        self.bottom_height = self.max_height/self.nb_tree_parts
        random.seed(self.seed)
        self.angle = math.radians(random.randint(-5, 5))
        self.factor = random.choice([-1, 1])
        self.speed = random.uniform(0.2, 0.6)
        self.can_move = True
        self.width_factor = 2
        self.last_c = Point2D.Point2D(0,0)
        self.last_d = Point2D.Point2D(0,0)

        self.nb_leaves = 10
        self.leaves_base_angle = 120
        self.leaves_start_angle = math.radians(180 + (180-self.leaves_base_angle)/2) # from right
        self.leaves_triangles_size = 50 * self.depth /normalScreenSize * pyautogui.size()[0]
        self.last_leaves_point = Point2D.Point2D(0,0)
        self.nb_triangles_by_leaves = 15
        self.triangle_leaves_rotation = math.radians(90/(self.nb_triangles_by_leaves - 1))

        self.coconuts = []
    def generate(self):
        self.all_triangles = []
        self.coconuts = []
        self.last_c = Point2D.Point2D(0, 0)
        self.last_d = Point2D.Point2D(0, 0)

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
                if i == self.nb_tree_parts - 1:
                    nbrCoconut = randint(3, 5)
                    centerX = self.last_c.x
                    centerY = self.last_c.y
                    for coconut in range(nbrCoconut):
                        if coconut == 0: #First coconut
                            size = randint(10/normalScreenSize * pyautogui.size()[0], 20/normalScreenSize * pyautogui.size()[0])
                            c1 = Coconut.Coconut( Point2D.Point2D(centerX, centerY), size)
                            c1.generate()
                            self.coconuts.append(c1)
                        else: #Other coconuts
                            size = randint(10/normalScreenSize * pyautogui.size()[0], 20/normalScreenSize * pyautogui.size()[0])
                            newCx = centerX + randint(size/2, size)
                            newCy = centerY + randint(size/2, size)
                            c1 = Coconut.Coconut( Point2D.Point2D(newCx, newCy), size)
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

        for tri in self.all_triangles:
            self.original_points.append((
                Point2D.Point2D(tri.a.x, tri.a.y),
                Point2D.Point2D(tri.b.x, tri.b.y),
                Point2D.Point2D(tri.c.x, tri.c.y)
            ))

    def color_for_trunk(self, triangle):
        altitude = triangle.a.y

        y_max = self.max_height
        y_min = self.position.y

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

    def update(self):
        if self.can_move:
            if math.radians(-5) < self.angle < math.radians(5):
                self.angle += math.radians(self.factor * self.speed)
            elif self.angle >= math.radians(5):
                self.factor = -1
                self.angle += math.radians(self.factor * self.speed)
            elif self.angle <= math.radians(-5):
                self.factor = 1
                self.angle += math.radians(self.factor * self.speed)

    def rotate_point2D(self, point, angle):
        cx = self.position.x
        cy = self.position.y
        s = math.sin(angle)
        c = math.cos(angle)
        x_new = c * (point.x - cx) - s * (point.y - cy) + cx
        y_new = s * (point.x - cx) + c * (point.y - cy) + cy
        return Point2D.Point2D(x_new, y_new)

    def manage_palm(self, window):
        self.update()
        for i,tri in enumerate(self.all_triangles):
            a_orig, b_orig, c_orig = self.original_points[i]
            tri.a = self.rotate_point2D(a_orig, self.angle)
            tri.b = self.rotate_point2D(b_orig, self.angle)
            tri.c = self.rotate_point2D(c_orig, self.angle)
            pygame.draw.polygon(window, tri.color, tri.to_pygame_point())

        for c in self.coconuts:
            for i,tri in enumerate(c.triangles):
                a_orig, b_orig, c_orig = c.original_triangles[i]
                tri.a = self.rotate_point2D(a_orig, self.angle)
                tri.b = self.rotate_point2D(b_orig, self.angle)
                tri.c = self.rotate_point2D(c_orig, self.angle)
            c.draw(window)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    test = PalmV2(Point2D.Point2D(screen.get_width()/2, screen.get_height()/2))
    test.generate()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks() / 1000.0

        screen.fill((255, 255, 255))
        test.manage_palm(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()