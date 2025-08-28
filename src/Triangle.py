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