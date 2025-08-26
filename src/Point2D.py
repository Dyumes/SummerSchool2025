class Point2D:
    def __init__(self, pos_x, pos_y):
        self.x = pos_x
        self.y = pos_y

    def display(self):
        print(f"position x: {self.x}, position y: {self.y}")