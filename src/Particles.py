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
SUN_PARTICLE_RADIUS = 5
PARTICLE_COLOR = (255, 100, 0)
SUN_PARTICLE_COLOR = (255, 255, 0)
SUN_PARTICLE_COLOR_DELTA = 150
#MIN_PARTICLES = 300
#MAX_PARTICLES = 300
GRAVITY_MAGNITUDE = 9.81
GRAVITY_DIRECTION = math.pi / 2
#HANDLING_PARTICLES_COLLISIONS = False
#HANDLING_OBJECTS_COLLISIONS = False
#HANDLING_SUN_COLLISIONS = True
SUN_GRAVITY_MAGNITUDE = 1


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
        """
            Check if a point is inside the circle.

            Args:
                point (Point): The point to check.

            Returns:
                bool: True if inside, False otherwise.
        """
        return (point[0] - self.center.x) ** 2 + (point[1] - self.center.y) ** 2 <= self.radius ** 2

    def draw(self, color=PARTICLE_COLOR):
        """
            Draw the circle as a polygon made of triangular slices.
        """
        for t in range(self.nbrTriangle):
            angle1 = (2 * math.pi * t) / self.nbrTriangle
            angle2 = (2 * math.pi * (t + 1)) / self.nbrTriangle

            pygame.draw.polygon(WINDOW, color, [[self.center.x, self.center.y],
                                                        [self.center.x + (self.radius * math.cos(angle1)),
                                                         self.center.y + (self.radius * math.sin(angle1))],
                                                        [self.center.x + (self.radius * math.cos(angle2)),
                                                         self.center.y + (self.radius * math.sin(angle2))]])

    def update(self, global_force):
        """
            Update the circle position based on a global force.

            Args:
                global_force (Force): The global force to apply.
        """
        #print("Updating circle at:", self.center.x, self.center.y)
        self.center = global_force.apply(Point(self.center.x, self.center.y))


class Vector:
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def add_vectors(self, other):
        """
            Add two vectors and return the resulting vector.

            Args:
                other (Vector): The vector to add.

            Returns:
                Vector: The resulting vector after addition.
        """

        x = self.magnitude * math.cos(self.direction) + other.magnitude * math.cos(other.direction)
        y = self.magnitude * math.sin(self.direction) + other.magnitude * math.sin(other.direction)
        return Vector(math.sqrt(x**2 + y**2), math.atan2(y, x))

class Force:
    def __init__(self, vector, name=None):
        self.vector = vector
        self.name = name

    def apply(self, point):
        """
            Apply force to a point and return the new position.

            Args:
                point (Point): The point where the force is applied.

            Returns:
                Point: The new point after applying the force.
        """

        return Point(
            point.x + self.vector.magnitude * math.cos(self.vector.direction),
            point.y + self.vector.magnitude * math.sin(self.vector.direction)
        )

    def add_forces(self, other):
        """
            Combine two forces into a single resultant force.

            Args:
                other (Force): The force to combine with.

            Returns:
                Force: The combined force.
        """
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
        self.is_colliding_w_sun = False

    def __del__(self):
        """
            Destructor for cleanup when the particle is removed.
        """
        #print("Particle deleted at:", self.form.center.x, self.form.center.y)
        del self

    def add_force(self, force):
        """
            Add a new force to the particle.

            Args:
                force (Force): The force to add.
        """

        self.forces.append(force)

    def combine_forces(self, forces):
        """
            Combine multiple forces into a single global force.

            Args:
                forces (list[Force]): List of forces to combine.
        """
        tmp_force = Force(Vector(0, 0))
        for force in forces:
            tmp_force = tmp_force.add_forces(force)

        self.global_force = tmp_force


    def reset_global_force(self):
        """
            Reset the global force acting on the particle.
        """
        self.global_force = Force(Vector(0, 0))

    def is_inside_env(self, env):
        """
            Check if the particle is inside the environment.

            Args:
                env (Environment): The environment to check against.

            Returns:
                bool: True if inside, False otherwise.
        """
        return env.is_inside(self.form.center)

    def touch_env_bottom(self, env):
        """
            Check if the particle touches the bottom of the environment.

            Args:
                env (Environment): The environment to check against.

            Returns:
                bool: True if touching, False otherwise.
        """
        if self.form.center.y + self.form.radius > env.height:
            return True
        return False

    def touch_env_border(self, env):
        """
            Check if the particle touches any environment border.

            Args:
                env (Environment): The environment to check against.

            Returns:
                bool: True if touching a border, False otherwise.
        """
        if self.form.center.x - self.form.radius < 0 or \
           self.form.center.x + self.form.radius > env.width or \
           self.form.center.y - self.form.radius < 0 or \
           self.form.center.y + self.form.radius > env.height:
            return True
        return False

    def bouncing(self, env):
        """
            Simulate particle bouncing when hitting the ground.
        """
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
        """
            Find a force by its name.

            Args:
                name (str): The name of the force.

            Returns:
                Force | None: The force if found, otherwise None.
        """
        for force in self.forces:
            if force.name == name:
                return force
        return None

    def change_force(self, name, change_magnitude, change_direction):
        """
            Modify an existing force's magnitude and/or direction.

            Args:
                name (str): Name of the force to change.
                change_magnitude (float): Value to add to the magnitude.
                change_direction (float): Value to add to the direction (radians).
        """
        force = self.find_force(name)
        if force is not None:
            #print("Changing force:", force)
            #print("Change magnitude:", change_magnitude, "Change direction:", change_direction)
            force.vector.magnitude += change_magnitude
            force.vector.direction += change_direction

    def is_colliding_with_particle(self, other):
        """
            Check if the particle is colliding with another particle.

            Args:
                other (Particle): Another particle to check collision with.

            Returns:
                bool: True if colliding, False otherwise.
        """
        distance = math.sqrt((self.form.center.x - other.form.center.x) ** 2 + (self.form.center.y - other.form.center.y) ** 2)
        return distance < (self.form.radius + other.form.radius)

    def colliding_with_particles(self, other):
        """
            Handle collision response with another particle.

            Args:
                other (Particle): The particle collided with.
        """
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
        """
            Check if the particle is inside a triangular object.

            Args:
                object (TestingObject): Object composed of triangles.

            Returns:
                tuple[bool, Triangle | None]: True and the triangle if inside,
                                              otherwise False and None.
        """

        def is_point_in_triangle(pt, v1, v2, v3):
            # Convertir les sommets en objets Point si nécessaire
            if isinstance(v1, tuple):
                v1 = Point(v1[0], v1[1])
            if isinstance(v2, tuple):
                v2 = Point(v2[0], v2[1])
            if isinstance(v3, tuple):
                v3 = Point(v3[0], v3[1])

            # Vérifie si un point est dans un triangle
            d1 = (pt.x - v1.x) * (v2.y - v1.y) - (v2.x - v1.x) * (pt.y - v1.y)
            d2 = (pt.x - v2.x) * (v3.y - v2.y) - (v3.x - v2.x) * (pt.y - v2.y)
            d3 = (pt.x - v3.x) * (v1.y - v3.y) - (v1.x - v3.x) * (pt.y - v3.y)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (has_neg and has_pos)

        def circle_intersects_segment(circle, p1, p2):
            # Vérifie si un cercle intersecte un segment
            cx, cy, r = circle.center.x, circle.center.y, circle.radius
            px, py = p1.x, p1.y
            qx, qy = p2.x, p2.y

            # Calcul de la distance entre le cercle et le segment
            dx, dy = qx - px, qy - py
            length_squared = dx * dx + dy * dy
            t = max(0, min(1, ((cx - px) * dx + (cy - py) * dy) / length_squared))
            nearest_x = px + t * dx
            nearest_y = py + t * dy
            dist_squared = (cx - nearest_x) ** 2 + (cy - nearest_y) ** 2
            return dist_squared <= r ** 2

        for triangle in object.triangles:
            pt = self.form.center
            a = triangle.get_position1()
            b = triangle.get_position2()
            c = triangle.get_position3()

            # Convertir les sommets en objets Point si nécessaire
            if isinstance(a, tuple):
                a = Point(a[0], a[1])
            if isinstance(b, tuple):
                b = Point(b[0], b[1])
            if isinstance(c, tuple):
                c = Point(c[0], c[1])

            # Vérifie si le centre est dans le triangle
            if is_point_in_triangle(pt, a, b, c):
                return True, triangle

            # Vérifie si le cercle intersecte un des côtés du triangle
            if circle_intersects_segment(self.form, a, b) or \
                    circle_intersects_segment(self.form, b, c) or \
                    circle_intersects_segment(self.form, c, a):
                return True, triangle

        return False, None

    def is_colliding_with_object(self, object):
        """
            Check if particle collides with an object.

            Args:
                object (TestingObject): Object to check collision with.

            Returns:
                tuple[bool, Triangle | None]: Collision info.
        """
        return self.is_inside_object(object)

    def colliding_with_objects(self, object_triangle):
        """
            Handle collision response with an object (triangle).

            Args:
                object_triangle (Triangle): The triangle the particle collides with.
        """

        def compute_closest_side_and_normal(triangle, point):
            # Trouve le côté le plus proche et calcule sa normale
            sides = [
                (triangle.get_position1(), triangle.get_position2()),
                (triangle.get_position2(), triangle.get_position3()),
                (triangle.get_position3(), triangle.get_position1())
            ]
            closest_side = None
            min_distance = float('inf')
            normal = None

            for p1, p2 in sides:
                # Convertir les sommets en objets Point si nécessaire
                if isinstance(p1, tuple):
                    p1 = Point(p1[0], p1[1])
                if isinstance(p2, tuple):
                    p2 = Point(p2[0], p2[1])

                # Projection du point sur le segment
                dx, dy = p2.x - p1.x, p2.y - p1.y
                length_squared = dx ** 2 + dy ** 2
                t = max(0, min(1, ((point.x - p1.x) * dx + (point.y - p1.y) * dy) / length_squared))
                nearest_x = p1.x + t * dx
                nearest_y = p1.y + t * dy

                # Distance au segment
                dist_squared = (point.x - nearest_x) ** 2 + (point.y - nearest_y) ** 2
                if dist_squared < min_distance:
                    min_distance = dist_squared
                    closest_side = (p1, p2)

                    # Calcul de la normale
                    normal_dx, normal_dy = -(p2.y - p1.y), (p2.x - p1.x)
                    normal_length = math.sqrt(normal_dx ** 2 + normal_dy ** 2)
                    normal = (normal_dx / normal_length, normal_dy / normal_length)

            return closest_side, normal

        # Trouver le côté le plus proche et sa normale
        closest_side, normal = compute_closest_side_and_normal(object_triangle, self.form.center)

        # Appliquer une force de rebond perpendiculaire au côté
        if normal:
            # Calcul de la direction de la normale
            normal_direction = math.atan2(normal[1], normal[0])

            # Inverser la composante perpendiculaire de la vitesse
            # incoming_velocity = self.global_force.vector
            # dot_product = (incoming_velocity.magnitude * math.cos(incoming_velocity.direction) * normal[0] +
            #                incoming_velocity.magnitude * math.sin(incoming_velocity.direction) * normal[1])
            # rebound_magnitude = max(1, abs(dot_product))
            rebound_magnitude = 5
            rebound_direction = normal_direction + math.pi  # Rebondir dans la direction opposée

            # Appliquer la force de rebond
            bounce_force = Force(Vector(rebound_magnitude, rebound_direction), "ObjectRebounce")
            self.add_force(bounce_force)

            if not self.is_colliding_with_objects:
                self.is_colliding_with_objects = True
                self.add_force(bounce_force)
            if self.is_colliding_with_objects:
                force = self.find_force("ObjectRebounce")
                if force is not None:
                    self.change_force("ObjectRebounce", change_magnitude=-0.5, change_direction=0)
                    if force.vector.magnitude <= 0:
                        self.forces.remove(force)
                        self.is_colliding_with_objects = False

    def decay_object_colliding_force(self):
        """
        Réduit progressivement et supprime la force de collision avec un objet après un certain temps.
        """
        force = self.find_force("ObjectRebounce")
        if force:
            # Réduction progressive de la magnitude
            force.vector.magnitude -= 0.3  # Taux de décroissance
            if force.vector.magnitude <= 0:
                self.forces.remove(force)
                self.is_colliding_with_objects = False

    def is_colliding_with_sun(self, sun):
        """
            Check if the particle is colliding with the sun.

            Args:
                sun (Sun): The sun object.

            Returns:
                bool: True if colliding, False otherwise.
        """
        dx = self.form.center.x - sun.centerX
        dy = self.form.center.y - sun.centerY
        distance = math.sqrt(dx * dx + dy * dy)

        sun_radius = sun.radius + sun.offset
        return distance < (sun_radius + self.form.radius)

    def colliding_with_sun(self, sun):
        """
        Handle collision response with the sun.

        Args:
            sun (Sun): The sun object.
        """
        dx = self.form.center.x - sun.centerX
        dy = self.form.center.y - sun.centerY
        distance = math.sqrt(dx * dx + dy * dy)
        direction = math.atan2(dy, dx)

        sun_radius = sun.radius + sun.offset

        if sun.is_static:
            # Put the particle outside the sun
            if distance < sun_radius + self.form.radius:
                overlap = (sun_radius + self.form.radius) - distance
                self.form.center.x += overlap * math.cos(direction)
                self.form.center.y += overlap * math.sin(direction)
            return

        # Calculer la direction d'éloignement du soleil
        #dx = self.form.center.x - sun.centerX
        #dy = self.form.center.y - sun.centerY
        #distance = math.sqrt(dx * dx + dy * dy)
        #direction = math.atan2(dy, dx)

        # # Reduce the bounce magnitude to make the rebounce less powerful
        # bounce_magnitude = 4 * (sun.radius + sun.offset - distance + self.form.radius) / self.form.radius
        # bounce_magnitude = max(bounce_magnitude, 1)  # Lower the minimum value to reduce power
        # Set a fixed bounce magnitude independent of particle size
        bounce_magnitude = 6  # Fixed value for rebounce power

        # Vérifier si on est déjà en train de rebondir
        if not self.is_colliding_w_sun:
            self.is_colliding_w_sun = True
            self.add_force(Force(Vector(bounce_magnitude, direction), "SunColliding"))
        else:
            # Mettre à jour la force de rebond si elle existe
            force = self.find_force("SunColliding")
            if force is not None:
                # print("Updating SunColliding force")
                #force.vector.magnitude = max(force.vector.magnitude, bounce_magnitude)
                #force.vector.direction = direction
                # Diminution progressive
                self.change_force("SunColliding", change_magnitude=-0.3, change_direction=0)
                if force.vector.magnitude <= 0:
                    self.forces.remove(force)
                    # print("Removing SunColliding force")
                    self.is_colliding_w_sun = False

    def apply_sun_gravity(self, sun):
        """
        Apply gravitational attraction from the sun.

        Args:
            sun (Sun): The sun object.
        """
        # Calculer la direction vers le soleil
        dx = sun.centerX - self.form.center.x
        dy = sun.centerY - self.form.center.y
        distance = math.sqrt(dx * dx + dy * dy)
        direction = math.atan2(dy, dx)

        # Force gravitationnelle inversement proportionnelle à la distance
        gravity_strength = SUN_GRAVITY_MAGNITUDE * 2000 / (distance + 50)

        # Mettre à jour la force existante ou en créer une nouvelle
        force = self.find_force("SunGravity")
        if force:
            force.vector.magnitude = min(gravity_strength, 2)  # Limiter la force maximale
            force.vector.direction = direction
        else:
            gravity_force = Force(Vector(min(gravity_strength, 5), direction), "SunGravity")
            self.add_force(gravity_force)

    def decay_sun_colliding_force(self):
        """
        Gradually decay and remove the 'SunColliding' force after a certain time.
        """
        force = self.find_force("SunColliding")
        if force:
            # Gradually reduce the magnitude
            force.vector.magnitude -= 0.1  # Decay rate
            if force.vector.magnitude <= 0:
                self.forces.remove(force)
                self.is_colliding_w_sun = False

    def draw(self, color=PARTICLE_COLOR):
        """
            Draw the particle.
        """
        self.form.draw(color=color)

    def update(self, env):
        """
        Update the particle state each frame.

        Args:
            env (Environment): The environment the particle is in.
        """
        self.combine_forces(self.forces)
        #print("Global force of: ", self.global_force)

        if not self.is_inside_env(env):
            env.remove_particle(self)
            #print("Particle is outside the environment, removing it.")
            self.__del__()

        if self.is_bouncing:
            self.bouncing(env)
        elif self.touch_env_bottom(env):
            #print("Particle touched the environment border at:", self.form.center.x, self.form.center.y)
            self.bouncing(env)

        self.form.update(self.global_force)
        self.decay_sun_colliding_force() # Fixes the problems with the sun collision force not being removed
        self.decay_object_colliding_force() # Fixes the problems with the object collision force not being removed
        #print("Forces on particle at:", self.form.center.x, self.form.center.y, "->", [force.name for force in self.forces])

class Environment:
    def __init__(self, size, sun=None):
        self.width = size[0]
        self.height = size[1]
        self.particles = []
        self.sun = sun
        self.handling_sun_collisions = False
        self.handling_objects_collisions = False
        self.handling_particles_collisions = False
        self.min_particles = 300
        self.max_particles = 300

    def is_inside(self, point):
        """
            Check if a point is inside the environment boundaries.

            Args:
                point (Point): The point to check.

            Returns:
                bool: True if inside, False otherwise.
        """

        return 0 <= point.x <= self.width and 0 <= point.y <= self.height

    def create_particle(self):
        """
            Create a new particle at a random location.

            Returns:
                Particle: The newly created particle.
        """
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        radius = CIRCLE_RADIUS
        self.particles.append(Particle(Circle(Point(x, y), radius, NBR_TRIANGLE_IN_CIRCLE)))
        #self.particles.append(Particle(Circle(Point(self.width // 2, 0), radius, NBR_TRIANGLE_IN_CIRCLE)))
        #print("Particle created at:", x, y)

    def create_particle_around_sun(self, sun):
        """
        Create a new particle at a random position around the sun.

        Args:
            sun (Sun): The sun object to spawn particles around.
        """
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(sun.radius, sun.radius + 50)
        x = sun.centerX + distance * math.cos(angle)
        y = sun.centerY + distance * math.sin(angle)
        radius = SUN_PARTICLE_RADIUS
        self.particles.append(Particle(Circle(Point(x, y), radius, NBR_TRIANGLE_IN_CIRCLE)))

    def remove_particle(self, particle):
        """
            Remove a particle from the environment.

            Args:
                particle (Particle): The particle to remove.
        """
        if particle in self.particles:
            self.particles.remove(particle)
            #print("Particle removed at:", particle.form.center.x, particle.form.center.y)
        else:
            print("Particle not found in environment.")

    def handle_particle_collisions(self):
        """
            Check and handle collisions between particles.
        """
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
        """
            Check and handle collisions between particles and objects.

            Args:
                objects: List of objects to check collisions with.
        """
        try:
            for i in range(len(self.particles)):
                for object in objects:
                    info = self.particles[i].is_colliding_with_object(object)
                    if info[0]:
                        #print("HIT")
                        self.particles[i].colliding_with_objects(info[1])

        except Exception as e:
            print("Erreur lors de la gestion des collisions avec les objets :", e)

    def handle_collisions_with_sun(self, sun):
        """
            Check and handle collisions between particles and the sun.

            Args:
                sun (Sun): The sun object.
        """
        try:
            for particle in self.particles:
                if particle.is_colliding_with_sun(sun):
                    particle.colliding_with_sun(sun)
        except Exception as e:
            print("Erreur lors de la gestion des collisions avec le soleil :", e)


    def draw(self):
        """
            Draw the environment and all its particles.
        """
        for particle in self.particles:
            color = PARTICLE_COLOR
            if self.handling_sun_collisions:
                # Change color based on distance to sun
                dx = particle.form.center.x - self.sun.centerX
                dy = particle.form.center.y - self.sun.centerY
                distance = math.sqrt(dx * dx + dy * dy)
                max_distance = (WINDOW_SIZE[0] + WINDOW_SIZE[1]) / 4
                intensity = max(0, 255 - int((distance / max_distance) * 255))
                color = (
                    max(0, min(255, SUN_PARTICLE_COLOR[0] + intensity * SUN_PARTICLE_COLOR_DELTA // 255)),
                    max(0, min(255, SUN_PARTICLE_COLOR[1] - intensity * SUN_PARTICLE_COLOR_DELTA // 255)),
                    max(0, min(255, SUN_PARTICLE_COLOR[2]))
                )
                #print("Color based on distance:", color)
            particle.draw(color)

    def update(self, objects=[]):
        """
            Update all particles in the environment.
        """
        if self.handling_particles_collisions:
            self.handle_particle_collisions()

        if self.handling_objects_collisions:
            self.handle_collisions_with_objects(objects)

        if self.handling_sun_collisions:
            self.handle_collisions_with_sun(self.sun)

        for particle in self.particles:
            particle.update(self)
            if self.sun is not None:
                particle.apply_sun_gravity(self.sun)


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


    class Sun:
        def __init__(self, centerX, centerY, nbrTriangle, radius):
            self.nbrTriangle = nbrTriangle
            self.radius = radius
            self.centerX = centerX
            self.centerY = centerY
            self.offset = 0
            self.maxReached = False
            self.previous_offset = None
            self.is_static = False

        def update(self, bpm):

            if not self.maxReached:
                self.offset += 1 * bpm / 60
                if self.offset >= 60:
                    self.offset = 60
                    self.maxReached = True
            else:
                self.offset -= 1 * bpm / 60
                if self.offset <= 0:
                    self.offset = 0
                    self.maxReached = False
            #self.previous_offset = self.offset

            if self.previous_offset == self.offset:
                self.is_static = True
            else:
                self.is_static = False

        def draw(self):
            for t in range(self.nbrTriangle):
                angle1 = (2 * math.pi * t) / self.nbrTriangle
                angle2 = (2 * math.pi * (t + 1)) / self.nbrTriangle
                midAngle = (angle1 + angle2) / 2

                endCenterX = self.centerX + ((self.offset) * math.cos(midAngle))
                endCenterY = self.centerY + ((self.offset) * math.sin(midAngle))

                x1 = endCenterX + ((self.radius + self.offset) * math.cos(angle1))
                y1 = endCenterY + ((self.radius + self.offset) * math.sin(angle1))
                x2 = endCenterX + ((self.radius + self.offset) * math.cos(angle2))
                y2 = endCenterY + ((self.radius + self.offset) * math.sin(angle2))

                pygame.draw.polygon(WINDOW, (255, 100, 0), [[self.centerX, self.centerY],
                                                            [self.centerX + (
                                                                        (self.radius + self.offset) * math.cos(angle1)),
                                                             self.centerY + ((self.radius + self.offset) * math.sin(
                                                                 angle1))],
                                                            [self.centerX + (
                                                                        (self.radius + self.offset) * math.cos(angle2)),
                                                             self.centerY + ((self.radius + self.offset) * math.sin(
                                                                 angle2))]])

                pygame.draw.polygon(WINDOW, (255, 167, 0), [[self.centerX, self.centerY], [x1, y1], [x2, y2]])

                pygame.draw.polygon(WINDOW, (255, 255, 0), [
                    [endCenterX, endCenterY], [x1, y1], [x2, y2]
                ])

    running = True

    env = Environment(WINDOW_SIZE)
    gravity = Force(Vector(GRAVITY_MAGNITUDE, GRAVITY_DIRECTION), "Gravity")
    #sun_gravity = Force(Vector(GRAVITY_MAGNITUDE / 2, GRAVITY_DIRECTION + math.pi / 2), "SunGravity")
    #forces = [gravity]
    #forces = []
    t1 = Triangle(
        (0, 0, 255),
        Point(WINDOW_SIZE[0] // 2 - 50, WINDOW_SIZE[1] // 2 - 50),
        Point(WINDOW_SIZE[0] // 2 + 50, WINDOW_SIZE[1] // 2 - 50),
        Point(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 50)
    )
    o1 = TestingObject([t1])

    s1 = Sun(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, 16, 100)
    # env.sun = s1
    # env.handling_sun_collisions = True
    env.handling_objects_collisions = True

    if env.handling_sun_collisions:
        for _ in range(random.randint(env.min_particles, env.max_particles)):
            env.create_particle_around_sun(s1)
    else:
        for _ in range(random.randint(env.min_particles, env.max_particles)):
            env.create_particle()


    for particle in env.particles:
        particle.add_force(gravity)
        #pass


    while running:

        WINDOW.fill((0, 0, 0))

        t1.draw()
        objects = [o1]

        # s1.draw()
        # s1.update(60)

        env.draw()
        env.update(objects)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                quit()


        CLOCK.tick(FPS)

        pygame.display.update()
