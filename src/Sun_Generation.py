import Triangle
import Point2D
import random
import pygame
import math

class SunV2():
    def __init__(self, center_point):
        self.circle_center = center_point
        self.original_center = Point2D.Point2D(center_point.x, center_point.y)
        self.original_triangles = []
        self.all_triangles = []
        self.nb_triangle_circle = 20
        self.circle_radius = 75
        self.seed = random.randint(0,10000)
        self.top_color = (255, 220, 120)
        self.bottom_color = (255, 70, 160)
        self.max_reached = False
        self.percentage = 0.5
        self.offset = 0

        self.ray_big_distance = self.circle_radius + 75
        self.ray_tiny_distance = self.circle_radius + 50
        self.ray_speed = 60
        self.ray_gap = 10

        self.music_duration = 10
        self.can_move = True

    def generate(self):
        angle = 2*math.pi/self.nb_triangle_circle

        for i in range(self.nb_triangle_circle):
            a = self.circle_center
            b = Point2D.Point2D(self.circle_center.x + self.circle_radius * math.cos(angle * i), self.circle_center.y + self.circle_radius * math.sin(angle * i))
            c = Point2D.Point2D(self.circle_center.x + self.circle_radius * math.cos(angle * (i+1)), self.circle_center.y + self.circle_radius * math.sin(angle * (i+1)))
            self.all_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0)))
            self.original_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0)))

        for i in range(self.nb_triangle_circle):
            if i % 2 == 0:
                a = Point2D.Point2D(self.circle_center.x + self.ray_big_distance * math.cos(angle * i + (angle * (i + 1) - angle * i) / 2), self.circle_center.y + self.ray_big_distance * math.sin(angle * i + (angle * (i + 1) - angle * i) / 2))
                b = Point2D.Point2D(self.circle_center.x + (self.circle_radius + self.ray_gap) * math.cos(angle * i), self.circle_center.y + (self.circle_radius + self.ray_gap) * math.sin(angle * i))
                c = Point2D.Point2D(self.circle_center.x + (self.circle_radius + self.ray_gap) * math.cos(angle * (i + 1)), self.circle_center.y + (self.circle_radius + self.ray_gap) * math.sin(angle * (i + 1)))
                self.all_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0), "ray_big"))
                self.original_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0), "ray_big"))
            else:
                a = Point2D.Point2D(self.circle_center.x + self.ray_tiny_distance * math.cos(angle * i + (angle * (i + 1) - angle * i) / 2), self.circle_center.y + self.ray_tiny_distance * math.sin(angle * i + (angle * (i + 1) - angle * i) / 2))
                b = Point2D.Point2D(self.circle_center.x + (self.circle_radius + self.ray_gap) * math.cos(angle * i), self.circle_center.y + (self.circle_radius + self.ray_gap) * math.sin(angle * i))
                c = Point2D.Point2D(self.circle_center.x + (self.circle_radius + self.ray_gap) * math.cos(angle * (i + 1)), self.circle_center.y + (self.circle_radius + self.ray_gap) * math.sin(angle * (i + 1)))
                self.all_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0), "ray_tiny"))
                self.original_triangles.append(Triangle.Triangle(a, b, c, (0, 0, 0), "ray_tiny"))


        for tri in self.all_triangles:
            self.color_for_triangle(tri)

    def color_for_triangle(self, triangle):
        altitude = max(triangle.b.y,triangle.c.y)
        y_max = self.circle_center.y - self.ray_big_distance
        y_min = self.circle_center.y + self.ray_big_distance

        t = (altitude - y_min)/(y_max - y_min)

        triangle.color = self.linear_interpolation_color(self.bottom_color,self.top_color, t)

    def linear_interpolation_color(self,color1, color2, factor):
        color = (int(color1[0] + (color2[0] - color1[0])*factor),
                 int(color1[1] + (color2[1] - color1[1])*factor),
                 int(color1[2] + (color2[2] - color1[2])*factor))

        return color

    def calc_position(self, current_time, screen_width, screen_height):
        factor = screen_width/self.music_duration
        pos_x = current_time * factor
        pos_y = pow(pos_x - screen_width/2, 2)/(pow(screen_width/2,2)/(1/8*screen_height + self.ray_big_distance)) + self.ray_big_distance

        return Point2D.Point2D(pos_x, pos_y)

    def update(self, bpm):
        if not self.max_reached:
            self.offset += 1 * bpm/60
            if self.offset >= 60:
                self.offset = 60
                self.max_reached = True
        else:
            self.offset -= 1 * bpm/60
            if self.offset <= 0:
                self.offset = 0
                self.max_reached = False

    def manage_sun(self, window, bpm, time):
        self.update(bpm)

        if self.can_move:
            self.circle_center = self.calc_position(time, window.get_width(), window.get_height())

        scale = 1 + (self.offset / 60) * self.percentage
        scale_ray_big = 1 + (self.offset/60) * self.percentage
        center_x = self.circle_center.x
        center_y = self.circle_center.y

        for i, tri in enumerate(self.all_triangles):
            original = self.original_triangles[i]

            if original.tag == "none":
                p1 = (center_x + (original.a.x - self.original_center.x) * scale, center_y + (original.a.y - self.original_center.y) * scale)
                p2 = (center_x + (original.b.x - self.original_center.x) * scale, center_y + (original.b.y - self.original_center.y) * scale)
                p3 = (center_x + (original.c.x - self.original_center.x) * scale, center_y + (original.c.y - self.original_center.y) * scale)
            elif original.tag == "ray_big":
                p1 = (center_x + (original.a.x - self.original_center.x) * scale_ray_big, center_y + (original.a.y - self.original_center.y) * scale_ray_big)
                p2 = (center_x + (original.b.x - self.original_center.x) * scale, center_y + (original.b.y - self.original_center.y) * scale)
                p3 = (center_x + (original.c.x - self.original_center.x) * scale, center_y + (original.c.y - self.original_center.y) * scale)
            else:
                p1 = (center_x + (original.a.x - self.original_center.x) * scale, center_y + (original.a.y - self.original_center.y) * scale)
                p2 = (center_x + (original.b.x - self.original_center.x) * scale, center_y + (original.b.y - self.original_center.y) * scale)
                p3 = (center_x + (original.c.x - self.original_center.x) * scale, center_y + (original.c.y - self.original_center.y) * scale)

            pygame.draw.polygon(window, tri.color, [p1,p2,p3])


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
        test.manage_sun(screen,60, current_time)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()