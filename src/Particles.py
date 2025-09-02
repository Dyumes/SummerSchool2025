import pygame
import random
from Quadtree import Quadtree, Rectangle
from Constants import *
import pyautogui

pygame.init()

#Display pygame with a bit smaller resolution than the screen itself no matter the os
WINDOW_SIZE = (pyautogui.size()[0] - 100, pyautogui.size()[1] - 100)
background_colour = (15, 0, 35)
WINDOW = pygame.display.set_mode(WINDOW_SIZE)

FPS = 60
CLOCK = pygame.time.Clock()
DT = CLOCK.tick(FPS) / 1000

NBR_TRIANGLE_IN_CIRCLE = 8
CIRCLE_RADIUS = 10 / 2560 * pyautogui.size()[0]
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
        return (point.x - self.center.x) ** 2 + (point.y - self.center.y) ** 2 <= self.radius ** 2

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
        if env.handling_sun_collisions:
            # Allow particles to go slightly outside the environment
            margin = MARGIN_SUN_PARTICLES
            return (-margin <= self.form.center.x <= env.width + margin and
                    -margin <= self.form.center.y <= env.height + margin)
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

        # Limit the position to stay within the environment
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
        # Compute vector of collision
        dx = other.form.center.x - self.form.center.x
        dy = other.form.center.y - self.form.center.y
        direction = math.atan2(dy, dx)

        # Relative speed
        relative_speed = abs(self.global_force.vector.magnitude - other.global_force.vector.magnitude)
        collide_magnitude = max(relative_speed, 10) # Ensure a minimum collision force

        # Collision force in the opposite direction
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
            # Convert tuples to Point objects if necessary
            if isinstance(v1, tuple):
                v1 = Point(v1[0], v1[1])
            if isinstance(v2, tuple):
                v2 = Point(v2[0], v2[1])
            if isinstance(v3, tuple):
                v3 = Point(v3[0], v3[1])

            # Check if point is in triangle
            d1 = (pt.x - v1.x) * (v2.y - v1.y) - (v2.x - v1.x) * (pt.y - v1.y)
            d2 = (pt.x - v2.x) * (v3.y - v2.y) - (v3.x - v2.x) * (pt.y - v2.y)
            d3 = (pt.x - v3.x) * (v1.y - v3.y) - (v1.x - v3.x) * (pt.y - v3.y)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (has_neg and has_pos)

        def circle_intersects_segment(circle, p1, p2):
            cx, cy, r = circle.center.x, circle.center.y, circle.radius
            px, py = p1.x, p1.y
            qx, qy = p2.x, p2.y

            # # Compute distance from circle center to segment
            dx, dy = qx - px, qy - py
            length_squared = dx * dx + dy * dy

            # Éviter la division par zéro
            if length_squared < 0.0000001:  # Presque zéro
                # Les points sont identiques, vérifier simplement la distance au point
                dist_squared = (cx - px) ** 2 + (cy - py) ** 2
                return dist_squared <= r ** 2

            t = max(0, min(1, ((cx - px) * dx + (cy - py) * dy) / length_squared))
            nearest_x = px + t * dx
            nearest_y = py + t * dy
            dist_squared = (cx - nearest_x) ** 2 + (cy - nearest_y) ** 2

            return dist_squared <= r ** 2

        # for triangle in object.triangles:
        #     pt = self.form.center
        #     a = triangle.get_position1()
        #     b = triangle.get_position2()
        #     c = triangle.get_position3()

        for triangle in object.all_triangles:
            pt = self.form.center
            a = triangle.a
            b = triangle.b
            c = triangle.c

            # Convert tuples to Point objects if necessary
            if isinstance(a, tuple):
                a = Point(a[0], a[1])
            if isinstance(b, tuple):
                b = Point(b[0], b[1])
            if isinstance(c, tuple):
                c = Point(c[0], c[1])

            if is_point_in_triangle(pt, a, b, c):
                return True, triangle

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
            # sides = [
            #     (triangle.get_position1(), triangle.get_position2()),
            #     (triangle.get_position2(), triangle.get_position3()),
            #     (triangle.get_position3(), triangle.get_position1())
            # ]
            sides = [
                (triangle.a, triangle.b),
                (triangle.b, triangle.c),
                (triangle.c, triangle.a)
            ]
            closest_side = None
            min_distance = float('inf')
            normal = None

            for p1, p2 in sides:
                if isinstance(p1, tuple):
                    p1 = Point(p1[0], p1[1])
                if isinstance(p2, tuple):
                    p2 = Point(p2[0], p2[1])

                # Projection of point onto the segment
                dx, dy = p2.x - p1.x, p2.y - p1.y
                length_squared = dx ** 2 + dy ** 2

                # Éviter la division par zéro
                if length_squared < 0.0000001:  # Presque zéro
                    # Les points sont identiques, vérifier simplement la distance au point
                    dist_squared = (point.x - p1.x) ** 2 + (point.y - p1.y) ** 2
                    if dist_squared < min_distance:
                        min_distance = dist_squared
                        closest_side = (p1, p2)
                        # Utiliser un vecteur normal par défaut (vers le haut)
                        normal = (0, 1)
                    continue

                t = max(0, min(1, ((point.x - p1.x) * dx + (point.y - p1.y) * dy) / length_squared))
                nearest_x = p1.x + t * dx
                nearest_y = p1.y + t * dy

                # Distance to segment
                dist_squared = (point.x - nearest_x) ** 2 + (point.y - nearest_y) ** 2
                if dist_squared < min_distance:
                    min_distance = dist_squared
                    closest_side = (p1, p2)

                    # Compute normal
                    normal_dx, normal_dy = -(p2.y - p1.y), (p2.x - p1.x)
                    normal_length = math.sqrt(normal_dx ** 2 + normal_dy ** 2)
                    normal = (normal_dx / normal_length, normal_dy / normal_length)

            return closest_side, normal

        closest_side, normal = compute_closest_side_and_normal(object_triangle, self.form.center)

        # Apply a rebound force perpendicular to the side
        if normal:
            normal_direction = math.atan2(normal[1], normal[0])

            # incoming_velocity = self.global_force.vector
            # dot_product = (incoming_velocity.magnitude * math.cos(incoming_velocity.direction) * normal[0] +
            #                incoming_velocity.magnitude * math.sin(incoming_velocity.direction) * normal[1])
            # rebound_magnitude = max(1, abs(dot_product))
            rebound_magnitude = 5
            rebound_direction = normal_direction + math.pi  # Rebound in the opposite direction

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
            Gradually reduces and removes the collision force with an object after a certain time.
        """
        force = self.find_force("ObjectRebounce")
        if force:
            force.vector.magnitude -= 0.3
            if force.vector.magnitude <= 0:
                self.forces.remove(force)
                self.is_colliding_with_objects = False

    def is_colliding_with_sun(self, sun):
        """
            Check if the particle is colliding with the sun.

            Args:
                sun: The sun object.

            Returns:
                bool: True if colliding, False otherwise.
        """
        if hasattr(sun, 'circle_radius'):
            dx = self.form.center.x - sun.circle_center.x
            dy = self.form.center.y - sun.circle_center.y
            distance = math.sqrt(dx * dx + dy * dy)
            sun_radius = sun.circle_radius + sun.offset

        else:
            dx = self.form.center.x - sun.centerX
            dy = self.form.center.y - sun.centerY
            distance = math.sqrt(dx * dx + dy * dy)
            sun_radius = sun.radius + sun.offset

        return distance < (sun_radius + self.form.radius)

    def colliding_with_sun(self, sun):
        """
            Handle collision response with the sun.

            Args:
                sun: The sun object.
        """
        if hasattr(sun, 'circle_center'):
            dx = self.form.center.x - sun.circle_center.x
            dy = self.form.center.y - sun.circle_center.y
            distance = math.sqrt(dx * dx + dy * dy)
            direction = math.atan2(dy, dx)
            sun_radius = sun.circle_radius + sun.offset

        else:
            dx = self.form.center.x - sun.centerX
            dy = self.form.center.y - sun.centerY
            distance = math.sqrt(dx * dx + dy * dy)
            direction = math.atan2(dy, dx)
            sun_radius = sun.radius + sun.offset

        if hasattr(sun, 'can_move'):
            if not sun.can_move:
                if distance < sun_radius + self.form.radius:
                    overlap = (sun_radius + self.form.radius) - distance
                    self.form.center.x += overlap * math.cos(direction)
                    self.form.center.y += overlap * math.sin(direction)
                return

        else:
            if sun.is_static:
                # Put the particle outside the sun
                if distance < sun_radius + self.form.radius:
                    overlap = (sun_radius + self.form.radius) - distance
                    self.form.center.x += overlap * math.cos(direction)
                    self.form.center.y += overlap * math.sin(direction)
                return

        # Compute direction away from sun center
        #dx = self.form.center.x - sun.centerX
        #dy = self.form.center.y - sun.centerY
        #distance = math.sqrt(dx * dx + dy * dy)
        #direction = math.atan2(dy, dx)

        # # Reduce the bounce magnitude to make the rebounce less powerful
        # bounce_magnitude = 4 * (sun.radius + sun.offset - distance + self.form.radius) / self.form.radius
        # bounce_magnitude = max(bounce_magnitude, 1)
        bounce_magnitude = 6
        random_angle = random.uniform(-0.5, 0.5)  # Perturbation angulaire
        perturbed_direction = direction + random_angle

        if not self.is_colliding_w_sun:
            self.is_colliding_w_sun = True
            self.add_force(Force(Vector(bounce_magnitude, perturbed_direction), "SunColliding"))
        else:
            force = self.find_force("SunColliding")
            if force is not None:
                # print("Updating SunColliding force")
                #force.vector.magnitude = max(force.vector.magnitude, bounce_magnitude)
                #force.vector.direction = direction

                self.change_force("SunColliding", change_magnitude=-0.3, change_direction=random.uniform(-0.1, 0.1))
                if force.vector.magnitude <= 0:
                    self.forces.remove(force)
                    # print("Removing SunColliding force")
                    self.is_colliding_w_sun = False

    def apply_sun_gravity(self, sun):
        """
            Apply gravitational attraction from the sun.

            Args:
                sun: The sun object.
        """
        # Compute vector from particle to sun
        if hasattr(sun, 'circle_center'):
            dx = sun.circle_center.x - self.form.center.x
            dy = sun.circle_center.y - self.form.center.y

        else:
            dx = sun.centerX - self.form.center.x
            dy = sun.centerY - self.form.center.y

        distance = math.sqrt(dx * dx + dy * dy)
        direction = math.atan2(dy, dx)

        # Gravity strength decreases with distance
        gravity_strength = SUN_GRAVITY_MAGNITUDE * 2000 / (distance + 50)

        # Ajouter un petit angle aléatoire à la direction
        random_angle = random.uniform(-0.1, 0.1)
        perturbed_direction = direction + random_angle

        force = self.find_force("SunGravity")
        if force:
            force.vector.magnitude = min(gravity_strength, 2)
            force.vector.direction = perturbed_direction
        else:
            gravity_force = Force(Vector(min(gravity_strength, 5), perturbed_direction), "SunGravity")
            self.add_force(gravity_force)

        # Ajouter une légère force tangentielle pour créer un mouvement orbital
        tangential_direction = direction + math.pi / 2
        tangential_strength = min(gravity_strength * 0.3, 0.5)

        force = self.find_force("SunOrbital")
        if force:
            force.vector.magnitude = tangential_strength
            force.vector.direction = tangential_direction
        else:
            orbital_force = Force(Vector(tangential_strength, tangential_direction), "SunOrbital")
            self.add_force(orbital_force)

    def decay_sun_colliding_force(self):
        """
            Gradually decay and remove the 'SunColliding' force after a certain time.
        """
        force = self.find_force("SunColliding")
        if force:
            force.vector.magnitude -= 0.1
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
        self.min_particles = MIN_PARTICLES
        self.max_particles = MAX_PARTICLES

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
                sun: The sun object to spawn particles around.
        """
        if hasattr(sun, 'circle_center'):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(sun.circle_radius, sun.circle_radius + 50)
            x = sun.circle_center.x + distance * math.cos(angle)
            y = sun.circle_center.y + distance * math.sin(angle)
            radius = SUN_PARTICLE_RADIUS
            self.particles.append(Particle(Circle(Point(x, y), radius, NBR_TRIANGLE_IN_CIRCLE)))

        else:
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
            print("Error while handling particle collisions:", e)

    def build_objects_quadtree(self, objects):
        """
        Construit un quadtree pour les objets de l'environnement
        """
        # Créer un nouveau quadtree couvrant tout l'environnement
        boundary = Rectangle(0, 0, self.width, self.height)
        self.objects_qtree = Quadtree(boundary, capacity=10)

        # Insérer les triangles des objets dans le quadtree
        for obj in objects:
            if not hasattr(obj, 'all_triangles'):
                continue

            for triangle in obj.all_triangles:
                # Créer un rectangle englobant pour le triangle
                points = []
                for point_attr in ['a', 'b', 'c']:
                    point = getattr(triangle, point_attr)
                    if isinstance(point, tuple):
                        points.append((point[0], point[1]))
                    else:
                        points.append((point.x, point.y))

                # Trouver les coordonnées min et max
                min_x = min(p[0] for p in points)
                max_x = max(p[0] for p in points)
                min_y = min(p[1] for p in points)
                max_y = max(p[1] for p in points)

                # Créer un rectangle englobant pour ce triangle
                triangle_rect = Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)

                # Stocker le triangle avec son rectangle englobant
                triangle.bounding_rect = triangle_rect
                triangle.parent_object = obj

                # Insérer dans le quadtree
                self.objects_qtree.insert(triangle)

    def handle_collisions_with_objects_optimized(self, objects):
        """
        Version optimisée de la détection de collision utilisant le quadtree
        """
        # Construire ou reconstruire le quadtree pour les objets
        self.build_objects_quadtree(objects)

        # Pour chaque particule
        for particle in self.particles:
            # Créer un rectangle de recherche autour de la particule
            search_radius = particle.form.radius * 2  # Zone de recherche un peu plus grande
            search_rect = Rectangle(
                particle.form.center.x - search_radius,
                particle.form.center.y - search_radius,
                search_radius * 2,
                search_radius * 2
            )

            # Trouver les triangles potentiellement en collision
            potential_triangles = self.objects_qtree.query(search_rect)

            # Vérifier les collisions avec ces triangles
            for triangle in potential_triangles:
                info = particle.is_colliding_with_object(triangle.parent_object)
                if info[0]:
                    particle.colliding_with_objects(info[1])
                    break  # On peut s'arrêter à la première collision

    def handle_collisions_with_objects(self, objects):
        """
            Check and handle collisions between particles and objects.

            Args:
                objects: List of objects to check collisions with.
        """
        try:
            for i in range(len(self.particles)):
                for object in objects:
                    # Vérifier si l'objet a la structure attendue pour la détection de collision
                    if not hasattr(object, 'all_triangles'):
                        continue

                    info = self.particles[i].is_colliding_with_object(object)
                    if info[0]:
                        #print("HIT")
                        self.particles[i].colliding_with_objects(info[1])

        except Exception as e:
            print("Error while handling collisions with objects:", e)

    def handle_collisions_with_sun(self, sun):
        """
            Check and handle collisions between particles and the sun.

            Args:
                sun: The sun object.
        """
        try:
            for particle in self.particles:
                if particle.is_colliding_with_sun(sun):
                    particle.colliding_with_sun(sun)
        except Exception as e:
            print("Error while handling collisions with the sun:", e)


    def draw(self):
        """
            Draw the environment and all its particles.
        """
        for particle in self.particles:
            color = PARTICLE_COLOR
            if self.handling_sun_collisions:

                if hasattr(self.sun, 'top_color'):
                    #print("The sun is a SunV2 instance, adjusting color based on position.")

                    top_color = self.sun.top_color
                    bottom_color = self.sun.bottom_color

                    y_top = self.sun.circle_center.y - self.sun.ray_big_distance
                    y_bottom = self.sun.circle_center.y + self.sun.ray_big_distance

                    # Interpolation factor based on vertical position
                    t = (particle.form.center.y - y_bottom) / (y_top - y_bottom)
                    t = max(0, min(t, 1))

                    # Linear interpolation
                    color = (
                        int(bottom_color[0] + (top_color[0] - bottom_color[0]) * t),
                        int(bottom_color[1] + (top_color[1] - bottom_color[1]) * t),
                        int(bottom_color[2] + (top_color[2] - bottom_color[2]) * t)
                    )

                else:
                    # Change color based on distance to sun
                    dx = particle.form.center.x - self.sun.centerX
                    dy = particle.form.center.y - self.sun.centerY
                    distance = math.sqrt(dx * dx + dy * dy)
                    max_distance = (WINDOW_SIZE[0] + WINDOW_SIZE[1]) / 8
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
            #self.handle_collisions_with_objects(objects)
            self.handle_collisions_with_objects_optimized(objects)

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
