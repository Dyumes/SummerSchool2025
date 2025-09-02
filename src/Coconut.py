from random import randint, random
import pygame
import math
import Point2D
import pyautogui
import Triangle

Coconuts = []

class Coconut():
    def __init__(self, center_point, radius):
        self.center_point = center_point
        self.radius = radius
        self.nbr_triangles = 20
        self.can_Break = False
        self.triangles = []
        self.original_triangles = []
        self.color = (115, 75, 20)

    def generate(self):
        Coconuts.append(self)
        angle = 2 * math.pi / self.nbr_triangles

        rx = self.radius * (1 + (random() - 0.5) * 0.3)
        ry = self.radius * (1 + (random() - 0.5) * 0.3)

        for i in range(self.nbr_triangles):
            a = self.center_point
            variation = 1 + 0.05 * math.sin(5 * i)  # petites bosses
            b =  Point2D.Point2D(self.center_point.x + rx * variation * math.cos(angle * i),
                 self.center_point.y + ry * variation * math.sin(angle * i))
            c =  Point2D.Point2D(self.center_point.x + rx * math.cos(angle * (i + 1)),
                 self.center_point.y + ry * math.sin(angle * (i + 1)))

            """
            red = randint(100, 130)
            green = randint(60, 90)
            blue = randint(15, 25)
            color = (red, green, blue)
            """
            #Version with light, has to be choose
            light_dir = (1, -1)
            dot = math.cos(angle * i) * light_dir[0] + math.sin(angle * i) * light_dir[1]
            brightness = int(30 * dot)
            color = (115 + brightness, 75 + brightness//2, 20)

            self.triangles.append(Triangle.Triangle(a, b, c, color))


        holeColor = (0, 0, 0)
        holeRadius = self.radius / 10

        r = randint(int(self.radius/4), int(self.radius/2))
        theta = random() * 2 * math.pi
        center_x = self.center_point.x + r * math.cos(theta)
        center_y = self.center_point.y + r * math.sin(theta)

        dist = holeRadius * randint(5, 7)/2
        base_angle = random() * 2 * math.pi

        for i in range(3):
            angle_i = base_angle + i * (2 * math.pi / 3)
            hx = center_x + dist * math.cos(angle_i)
            hy = center_y + dist * math.sin(angle_i)
            self.make_hole(hx, hy, holeRadius, holeColor)

        for tri in self.triangles:
            self.original_triangles.append((
                Point2D.Point2D(tri.a.x, tri.a.y),
                Point2D.Point2D(tri.b.x, tri.b.y),
                Point2D.Point2D(tri.c.x, tri.c.y)
            ))

    def make_hole(self, cx, cy, holeRadius, holeColor):
        step_angle = 2 * math.pi / 10
        for i in range(10):
            a = Point2D.Point2D(cx, cy)
            b = Point2D.Point2D(cx + holeRadius * math.cos(step_angle * i),
                 cy + holeRadius * math.sin(step_angle * i))
            c = Point2D.Point2D(cx + holeRadius * math.cos(step_angle * (i + 1)),
                 cy + holeRadius * math.sin(step_angle * (i + 1)))
            self.triangles.append(Triangle.Triangle(a, b, c, holeColor))

    def draw(self, window):
        for t in self.triangles:
            pygame.draw.polygon(window, t.color, t.to_pygame_point())

def clean(window):
    Coconuts.clear()
    window.fill((0, 0, 0))

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((pyautogui.size()[0] - 100, pyautogui.size()[1] - 100))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                match event.key :
                    case pygame.K_r:
                        print("SHOULD CREATE A COCONUT")
                        clean(screen)
                        coco1 = Coconut((pyautogui.size()[0] / 2, pyautogui.size()[1]/2), 30)
                        coco1.generate()

        screen.fill((255, 255, 255))
        for c in Coconuts:
            c.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
