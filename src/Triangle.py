import math
import Point2D

class Triangle:
    def __init__(self,corner_a, corner_b, corner_c, color, tag="none"):
        self.a = corner_a
        self.b = corner_b
        self.c = corner_c
        self.color = color
        self.tag = tag

    def to_pygame_point(self):
        return [(self.a.x, self.a.y),
                (self.b.x, self.b.y),
                (self.c.x, self.c.y)]

def get_triangle_from_center(center_point, angle, side_lenght, tag="none"):
    radius = side_lenght / math.sqrt(3)
    return Triangle(
        Point2D.Point2D(center_point.x + radius * math.cos(angle), center_point.y + radius * math.sin(angle)),
        Point2D.Point2D(center_point.x + radius * math.cos(angle + math.radians(120)),
                        center_point.y + radius * math.sin(angle + math.radians(120))),
        Point2D.Point2D(center_point.x + radius * math.cos(angle + math.radians(240)),
                        center_point.y + radius * math.sin(angle + math.radians(240))),
        (0, 0, 0), tag)
