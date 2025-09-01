from sympy.codegen.scipy_nodes import powm1

from Triangle import Triangle
import Point2D
import random
import pygame
import math
import pyautogui

class Robot():
    def __init__(self, center_point):
        self.center_point = center_point


class Robot_Head():
    def __init__(self, center_point : Point2D):
        self.center_point = center_point
        self.width = 100
        self.height = 100
        self.triangles = []

    #Type 1 head : Square
    def generateSquare(self):
        p1 = (self.center_point.x - self.width / 2, self.center_point.y + self.height / 2)
        p2 = (self.center_point.x - self.width / 2, self.center_point.y - self.height / 2)
        p3 = (self.center_point.x + self.width / 2, self.center_point.y + self.height / 2)
        p4 = (self.center_point.x + self.width / 2, self.center_point.y - self.height / 2)

        color = (125, 125, 125)
        t1 = Triangle(p1, p2, p3, color)
        t2 = Triangle(p2, p3, p4, color)

        self.triangles.append(t1)
        self.triangles.append(t2)

    #Type 2 head : Rectangle + demi-circle
    def generateRect_Circle(self):
        pass


    def draw(self, window):
        print("DRAWING")
        color = 125, 125, 125
        for t in self.triangles :
            pygame.draw.polygon(window, color, [t.a, t.b, t.c])


windowWidth = pyautogui.size()[0] - 100
windowHeight = pyautogui.size()[1] - 100
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    head1 = Robot_Head(Point2D.Point2D(300, 300))
    head1.generateSquare()
    head2 = Robot_Head(Point2D.Point2D(500, 500))
    head2.generateRect_Circle()
    #test = SunV2(Point2D.Point2D(screen.get_width()/2, screen.get_height()/2))
    #test.generate()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks() / 1000.0

        screen.fill((255, 255, 255))
        head1.draw(screen)
        head2.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()