import Triangle
import Point2D
import random
import pygame
import math

class SunV2():
    def __init__(self, center_point):
        self.circle_center = center_point
        self.all_triangles = []
        self.nb_triangle_circle = 100
        self.circle_radius = 500
        self.seed = random.randint(0,10000)
        self.top_color = (255, 220, 120)
        self.bottom_color = (255, 70, 160)

    def generate(self):
        random.seed(self.seed)

        angle = 2*math.pi/self.nb_triangle_circle

        for i in range(self.nb_triangle_circle):
            a = self.circle_center
            b = Point2D.Point2D(self.circle_center.x + self.circle_radius * math.cos(angle * i),self.circle_center.y + self.circle_radius * math.sin(angle * i))
            c = Point2D.Point2D(self.circle_center.x + self.circle_radius * math.cos(angle * (i+1)),self.circle_center.y + self.circle_radius * math.sin(angle * (i+1)))
            self.all_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0)))

        for tri in self.all_triangles:
            self.color_for_triangle(tri)

    def color_for_triangle(self, triangle):
        altitude = max(triangle.b.y,triangle.c.y)
        t = (altitude - (self.circle_radius + self.circle_center.y))/(self.circle_radius - self.circle_center.y - (self.circle_radius + self.circle_center.y))

        triangle.color = self.linear_interpolation_color(self.bottom_color,self.top_color, t)

    def linear_interpolation_color(self,color1, color2, factor):
        color = (int(color1[0] + (color2[0] - color1[0])*factor),
                 int(color1[1] + (color2[1] - color1[1])*factor),
                 int(color1[2] + (color2[2] - color1[2])*factor))

        return color

    def update(self):
        print("TODO")

    def manage_sun(self, screen, time):
        print("TODO")

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    clock = pygame.time.Clock()
    test = SunV2(Point2D.Point2D(screen.get_width()/2, screen.get_height()/2))
    test.generate()


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = pygame.time.get_ticks() / 1000.0

        screen.fill((255, 255, 255))

        for tri in test.all_triangles:
            pygame.draw.polygon(screen,tri.color,tri.to_pygame_point())

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()