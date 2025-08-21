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
MIN_PARTICLES = 1
MAX_PARTICLES = 10

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

    def update(self, global_force):
        print("Updating circle at:", self.center.x, self.center.y)
        self.center = global_force.apply(Point(self.center.x, self.center.y))


class Vector:
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def add_vectors(self, other):
        x = self.magnitude * math.cos(self.direction) + other.magnitude * math.cos(other.direction)
        y = self.magnitude * math.sin(self.direction) + other.magnitude * math.sin(other.direction)
        return Vector(math.sqrt(x**2 + y**2), math.atan2(y, x))

class Force:
    def __init__(self, vector, name=None):
        self.vector = vector
        self.name = name

    def apply(self, point):
        return Point(
            point.x + self.vector.magnitude * math.cos(self.vector.direction),
            point.y + self.vector.magnitude * math.sin(self.vector.direction)
        )

    def add_forces(self, other):
        return Force(self.vector.add_vectors(other.vector))

    def __str__(self):
        return f"Force with magnitude {self.vector.magnitude} and direction {self.vector.direction} radians"

class Particle:
    def __init__(self, form, forces=None):
        if forces is None:
            forces = [Force(Vector(0, 0))]
        self.form = form
        self.forces = forces
        self.global_force = Force(Vector(0, 0))
        self.is_bouncing = False

    def __del__(self):
        print("Particle deleted at:", self.form.center.x, self.form.center.y)
        del self

    def add_force(self, force):
        self.forces.append(force)

    def combine_forces(self, forces):
        tmp_force = Force(Vector(0, 0))
        for force in forces:
            tmp_force = tmp_force.add_forces(force)

        self.global_force = tmp_force


    def reset_global_force(self):
        self.global_force = Force(Vector(0, 0))

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
            rebounce_force = Force(Vector(20, -math.pi / 2), "GroundRebounce")
            self.add_force(rebounce_force)
        if self.is_bouncing:
            force = self.find_force("GroundRebounce")
            if force is not None:
                self.change_force("GroundRebounce", change_magnitude=-0.5, change_direction=0)
                if force.vector.magnitude <= 0:
                    self.forces.remove(force)  # Supprimer la force de rebond
                    self.is_bouncing = False
                    print("Particle stopped bouncing at:", self.form.center.x, self.form.center.y)

        # Limite la position pour rester dans l'environnement
        self.form.center.x = max(self.form.radius, min(self.form.center.x, env.width - self.form.radius))
        self.form.center.y = max(self.form.radius, min(self.form.center.y, env.height - self.form.radius))

    def find_force(self, name):
        for force in self.forces:
            if force.name == name:
                return force
        return None

    def change_force(self, name, change_magnitude, change_direction):
        force = self.find_force(name)
        if force is not None:
            print("Changing force:", force)
            print("Change magnitude:", change_magnitude, "Change direction:", change_direction)
            force.vector.magnitude += change_magnitude
            force.vector.direction += change_direction

    def is_colliding(self, other):
        distance = math.sqrt((self.form.center.x - other.form.center.x) ** 2 + (self.form.center.y - other.form.center.y) ** 2)
        return distance < (self.form.radius + other.form.radius)

    def draw(self):
        self.form.draw()

    def update(self, env):
        self.combine_forces(self.forces)
        print("Global force of: ", self.global_force)
        #self.form.update(self.global_force)
        if not self.is_inside_env(env):
            env.remove_particle(self)
            print("Particle is outside the environment, removing it.")
            self.__del__()

        if self.is_bouncing:
            self.bouncing()
        elif self.touch_env_border(env):
            print("Particle touched the environment border at:", self.form.center.x, self.form.center.y)
            self.bouncing()

        self.form.update(self.global_force)

class Environment:
    def __init__(self, size):
        self.width = size[0]
        self.height = size[1]
        self.particles = []

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

    def handle_particle_collisions(self):
        try:
            for i in range(len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    if self.particles[i].is_colliding(self.particles[j]):
                        print("Collision detected between particles at:", self.particles[i].form.center.x,
                              self.particles[i].form.center.y,
                              "and", self.particles[j].form.center.x, self.particles[j].form.center.y)

                        self.remove_particle(self.particles[i])
        except Exception as e:
            print("Erreur lors de la gestion des collisions de particules :", e)

    def draw(self):
        for particle in self.particles:
            particle.draw()

    def update(self):
        for particle in self.particles:
            particle.update(self)

        self.handle_particle_collisions()


if __name__ == "__main__":

    running = True

    env = Environment(WINDOW_SIZE)
    #c1 = Circle(Point(100, 100), 20, NBR_TRIANGLE_IN_CIRCLE)
    gravity = Force(Vector(9.81, math.pi / 2))  # Gravity vector pointing downwards
    forces = [gravity]
    #p1 = Particle(c1)
    #p1.add_force(gravity)

    for _ in range(random.randint(MIN_PARTICLES, MAX_PARTICLES)):
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