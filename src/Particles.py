import pygame
import math
import random
from win32api import GetSystemMetrics


pygame.init()

#Display pygame with a bit smaller resolution than the screen itself no matter the os
WINDOW_SIZE = (GetSystemMetrics(0) - 100, GetSystemMetrics(1) - 100)
WINDOW = pygame.display.set_mode(WINDOW_SIZE)

FPS = 60
CLOCK = pygame.time.Clock()
DT = CLOCK.tick(FPS) / 1000

NBR_TRIANGLE_IN_CIRCLE = 6

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Circle:
    def __init__(self, center, radius, nbrTriangle):
        self.center = center
        self.radius = radius
        self.nbrTriangle = nbrTriangle

    def contains(self, point):
        return (point[0] - self.center.x) ** 2 + (point[1] - self.center.y) ** 2 <= self.radius ** 2

    def draw(self):
        for t in range(self.nbrTriangle):
            angle1 = (2 * math.pi * t) / self.nbrTriangle
            angle2 = (2 * math.pi * (t + 1)) / self.nbrTriangle

            pygame.draw.polygon(WINDOW, (255, 100, 0), [[self.center.x, self.center.y],
                                                        [self.center.x + (self.radius * math.cos(angle1)),
                                                         self.center.y + (self.radius * math.sin(angle1))],
                                                        [self.center.x + (self.radius * math.cos(angle2)),
                                                         self.center.y + (self.radius * math.sin(angle2))]])

    def update(self, forces):
        if forces is not None:
            print("Updating circle at:", self.center.x, self.center.y)
            for force in forces:
                self.center = force.apply(Point(self.center.x, self.center.y))


class Vector:
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

class Force:
    def __init__(self, vector):
        self.vector = vector

    def apply(self, point):
        return Point(
            point.x + self.vector.magnitude * math.cos(self.vector.direction),
            point.y + self.vector.magnitude * math.sin(self.vector.direction)
        )

class Particle:
    def __init__(self, form, forces=None):
        if forces is None:
            forces = []
        self.form = form
        self.forces = forces
        self.is_bouncing = False

    def __del__(self):
        print("Particle deleted at:", self.form.center.x, self.form.center.y)
        del self

    def draw(self):
        self.form.draw()

    def update(self, env):
        self.form.update(self.forces)
        if not self.is_inside_env(env):
            env.remove_particle(self)
            print("Particle is outside the environment, removing it.")
            self.__del__()

        if self.touch_env_border(env):
            print("Particle touched the environment border at:", self.form.center.x, self.form.center.y)
            self.bouncing()

    def add_force(self, force):
        if self.forces is None:
            self.forces = []
        self.forces.append(force)

    def is_inside_env(self, env):
        return env.is_inside(self.form.center)

    def touch_env_border(self, env):
        if self.form.center.x - self.form.radius < 0 or \
           self.form.center.x + self.form.radius > env.width or \
           self.form.center.y - self.form.radius < 0 or \
           self.form.center.y + self.form.radius > env.height:
            return True
        return False

    def bouncing(self):
        if not self.is_bouncing:
            self.is_bouncing = True
            print("Particle is bouncing at:", self.form.center.x, self.form.center.y)
            #TODO

class Environment:
    def __init__(self, size):
        self.width = size[0]
        self.height = size[1]
        self.particles = []

    def draw(self):
        for particle in self.particles:
            particle.draw()

    def update(self):
        for particle in self.particles:
            particle.update(self)

    def is_inside(self, point):
        return 0 <= point.x <= self.width and 0 <= point.y <= self.height

    def create_particle(self):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        radius = 20
        self.particles.append(Particle(Circle(Point(x, y), radius, NBR_TRIANGLE_IN_CIRCLE)))
        print("Particle created at:", x, y)

    def remove_particle(self, particle):
        if particle in self.particles:
            self.particles.remove(particle)
            print("Particle removed at:", particle.form.center.x, particle.form.center.y)
        else:
            print("Particle not found in environment.")



if __name__ == "__main__":

    running = True

    env = Environment(WINDOW_SIZE)
    #c1 = Circle(Point(100, 100), 20, NBR_TRIANGLE_IN_CIRCLE)
    gravity = Force(Vector(9.81, math.pi / 2))  # Gravity vector pointing downwards
    forces = [gravity]
    #p1 = Particle(c1)
    #p1.add_force(gravity)
    env.create_particle()
    for particle in env.particles:
        particle.add_force(gravity)


    while running:

        WINDOW.fill((0, 0, 0))
        #c1.draw()
        #c1.update(forces)
        env.draw()
        env.update()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                quit()


        CLOCK.tick(FPS)

        pygame.display.update()