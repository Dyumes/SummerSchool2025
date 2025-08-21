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

NBR_TRIANGLE_IN_CIRCLE = 8
CIRCLE_RADIUS = 10
MIN_PARTICLES = 50
MAX_PARTICLES = 100
GRAVITY_MAGNITUDE = 9.81
GRAVITY_DIRECTION = math.pi / 2
HANDLING_PARTICLES_COLLISIONS = True
HANDLING_OBJECTS_COLLISIONS = True


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
        #print("Updating circle at:", self.center.x, self.center.y)
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
        self.is_colliding_with_particles = False
        self.is_colliding_with_objects = False

    def __del__(self):
        #print("Particle deleted at:", self.form.center.x, self.form.center.y)
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

    def touch_env_bottom(self, env):
        if self.form.center.y + self.form.radius > env.height:
            return True
        return False

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
            #print("Particle is bouncing at:", self.form.center.x, self.form.center.y)
            rebounce_force = Force(Vector(20, -math.pi / 2), "GroundRebounce")
            self.add_force(rebounce_force)
        if self.is_bouncing:
            force = self.find_force("GroundRebounce")
            if force is not None:
                self.change_force("GroundRebounce", change_magnitude=-0.5, change_direction=0)
                if force.vector.magnitude <= 0:
                    self.forces.remove(force)  # Supprimer la force de rebond
                    self.is_bouncing = False
                    #print("Particle stopped bouncing at:", self.form.center.x, self.form.center.y)

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
            #print("Changing force:", force)
            #print("Change magnitude:", change_magnitude, "Change direction:", change_direction)
            force.vector.magnitude += change_magnitude
            force.vector.direction += change_direction

    def is_colliding_with_particle(self, other):
        distance = math.sqrt((self.form.center.x - other.form.center.x) ** 2 + (self.form.center.y - other.form.center.y) ** 2)
        return distance < (self.form.radius + other.form.radius)

    def colliding_with_particles(self, other):
        # Calcul du vecteur de collision
        dx = other.form.center.x - self.form.center.x
        dy = other.form.center.y - self.form.center.y
        direction = math.atan2(dy, dx)

        # Vitesse relative (ici, on utilise la magnitude du global_force)
        relative_speed = abs(self.global_force.vector.magnitude - other.global_force.vector.magnitude)
        collide_magnitude = max(relative_speed, 10)  # Valeur minimale pour éviter 0

        # Force de collision opposée au contact
        collide_force = Force(Vector(collide_magnitude, direction + math.pi), "Colliding")
        self.add_force(collide_force)

        if not self.is_colliding_with_particles:
            self.is_colliding_with_particles = True
        if self.is_colliding_with_particles:
            force = self.find_force("Colliding")
            if force is not None:
                self.change_force("Colliding", change_magnitude=-0.5, change_direction=0)
                if force.vector.magnitude <= 0:
                    self.forces.remove(force)
                    self.is_colliding_with_particles = False
                    #print("Particle stopped colliding at:", self.form.center.x, self.form.center.y)

    def is_inside_object(self, object):
        # Détection si le centre de la particule est à l'intérieur d'un des triangles de l'objet
        for triangle in object.triangles:
            def sign(p1, p2, p3):
                return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)

            pt = self.form.center
            a = triangle.get_position1()
            b = triangle.get_position2()
            c = triangle.get_position3()
            d1 = sign(pt, a, b)
            d2 = sign(pt, b, c)
            d3 = sign(pt, c, a)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (has_neg and has_pos):
                return True, triangle
        return False, None

    def is_colliding_with_object(self, object):
        return self.is_inside_object(object)

    def colliding_with_objects(self, object_triangle):
        #TODO
        def compute_center(triangle):
            return Point(
                (triangle.get_position1().x + triangle.get_position2().x + triangle.get_position3().x) / 3,
                (triangle.get_position1().y + triangle.get_position2().y + triangle.get_position3().y) / 3
            )

        # Calcul du vecteur de collision
        triangle_center = compute_center(object_triangle)
        dx = triangle_center.x - self.form.center.x
        dy = triangle_center.y - self.form.center.y
        direction = math.atan2(dy, dx)

        # Vitesse relative (ici, on utilise la magnitude du global_force)
        relative_speed = abs(self.global_force.vector.magnitude - 0.2) # Pour simuler une absorption de la vitesse
        collide_magnitude = max(relative_speed, 10)  # Valeur minimale pour éviter 0

        # Force de collision opposée au contact
        collide_force = Force(Vector(collide_magnitude, direction + math.pi), "ObjectColliding")
        self.add_force(collide_force)

        if not self.is_colliding_with_objects:
            self.is_colliding_with_objects = True
        if self.is_colliding_with_objects:
            force = self.find_force("ObjectColliding")
            if force is not None:
                self.change_force("ObjectColliding", change_magnitude=-0.5, change_direction=0)
                if force.vector.magnitude <= 0:
                    self.forces.remove(force)
                    self.is_colliding_with_objects = False

    def draw(self):
        self.form.draw()

    def update(self, env):
        self.combine_forces(self.forces)
        #print("Global force of: ", self.global_force)

        if not self.is_inside_env(env):
            env.remove_particle(self)
            #print("Particle is outside the environment, removing it.")
            self.__del__()

        if self.is_bouncing:
            self.bouncing()
        elif self.touch_env_bottom(env):
            #print("Particle touched the environment border at:", self.form.center.x, self.form.center.y)
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
        radius = CIRCLE_RADIUS
        self.particles.append(Particle(Circle(Point(x, y), radius, NBR_TRIANGLE_IN_CIRCLE)))
        #print("Particle created at:", x, y)

    def remove_particle(self, particle):
        if particle in self.particles:
            self.particles.remove(particle)
            #print("Particle removed at:", particle.form.center.x, particle.form.center.y)
        else:
            print("Particle not found in environment.")

    def handle_particle_collisions(self):
        try:
            for i in range(len(self.particles)):
                for j in range(i + 1, len(self.particles)):
                    if self.particles[i].is_colliding_with_particle(self.particles[j]):
                        #print("Collision detected between particles at:", self.particles[i].form.center.x, self.particles[i].form.center.y, "and", self.particles[j].form.center.x, self.particles[j].form.center.y)

                        #self.remove_particle(self.particles[i])
                        self.particles[i].colliding_with_particles(self.particles[j])
                        self.particles[j].colliding_with_particles(self.particles[i])

        except Exception as e:
            print("Erreur lors de la gestion des collisions de particules :", e)

    def handle_collisions_with_objects(self, objects):
        try:
            for i in range(len(self.particles)):
                for object in objects:
                    info = self.particles[i].is_colliding_with_object(object)
                    if info[0]:
                        print("HIT")
                        self.particles[i].colliding_with_objects(info[1])

        except Exception as e:
            print("Erreur lors de la gestion des collisions avec les objets :", e)


    def draw(self):
        for particle in self.particles:
            particle.draw()

    def update(self, objects=[]):
        for particle in self.particles:
            particle.update(self)

        if HANDLING_PARTICLES_COLLISIONS:
            self.handle_particle_collisions()

        if HANDLING_OBJECTS_COLLISIONS:
            self.handle_collisions_with_objects(objects)


if __name__ == "__main__":

    """ For testing purposes"""
    class Triangle:
        def __init__(self, color, p1, p2, p3):
            self.color = color
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.sides = [(p1, p2), (p1, p3), (p2, p3)]

        def get_color(self):
            returnList = [self.color[0], self.color[1], self.color[2]]
            return returnList

        def get_position1(self):
            return self.p1

        def get_position2(self):
            return self.p2

        def get_position3(self):
            return self.p3

        def draw(self):
            pygame.draw.polygon(
                WINDOW,
                self.color,
                [(self.p1.x, self.p1.y), (self.p2.x, self.p2.y), (self.p3.x, self.p3.y)]
            )

    class TestingObject:
        def __init__(self, triangles):
            self.triangles = triangles


    running = True

    env = Environment(WINDOW_SIZE)
    gravity = Force(Vector(GRAVITY_MAGNITUDE, GRAVITY_DIRECTION))
    forces = [gravity]
    t1 = Triangle(
        (0, 0, 255),
        Point(WINDOW_SIZE[0] // 2 - 50, WINDOW_SIZE[1] // 2 - 50),
        Point(WINDOW_SIZE[0] // 2 + 50, WINDOW_SIZE[1] // 2 - 50),
        Point(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50)
    )
    o1 = TestingObject([t1])

    for _ in range(random.randint(MIN_PARTICLES, MAX_PARTICLES)):
        env.create_particle()


    for particle in env.particles:
        particle.add_force(gravity)


    while running:

        WINDOW.fill((0, 0, 0))

        t1.draw()
        objects = [o1]

        env.draw()
        env.update(objects)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                quit()


        CLOCK.tick(FPS)

        pygame.display.update()