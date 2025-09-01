class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, point):
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)

    def intersects(self, other):
        return not (other.x > self.x + self.width or
                    other.x + other.width < self.x or
                    other.y > self.y + self.height or
                    other.y + other.height < self.y)


class Quadtree:
    def __init__(self, boundary, capacity=4):
        self.boundary = boundary
        self.capacity = capacity
        self.particles = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def insert(self, item):
            # Vérifier si c'est une particule ou un triangle
            if hasattr(item, 'form'):
                # C'est une particule
                if not self.boundary.contains(item.form.center):
                    return False
            elif hasattr(item, 'bounding_rect'):
                # C'est un triangle avec un rectangle englobant
                if not self.boundary.intersects(item.bounding_rect):
                    return False
            else:
                # Type non supporté
                return False

            # Si nous avons encore de la place et que nous ne sommes pas divisés
            if len(self.particles) < self.capacity and not self.divided:
                self.particles.append(item)
                return True

            # Sinon, on divise et on insère dans les sous-quadrants
            if not self.divided:
                self.subdivide()

            # Essayer d'insérer dans chaque sous-quadrant
            if (self.northwest.insert(item) or self.northeast.insert(item) or
                    self.southwest.insert(item) or self.southeast.insert(item)):
                return True

            return False

    def subdivide(self):
        x = self.boundary.x
        y = self.boundary.y
        w = self.boundary.width / 2
        h = self.boundary.height / 2

        nw = Rectangle(x, y, w, h)
        ne = Rectangle(x + w, y, w, h)
        sw = Rectangle(x, y + h, w, h)
        se = Rectangle(x + w, y + h, w, h)

        self.northwest = Quadtree(nw, self.capacity)
        self.northeast = Quadtree(ne, self.capacity)
        self.southwest = Quadtree(sw, self.capacity)
        self.southeast = Quadtree(se, self.capacity)

        # Déplacer les particules existantes vers les sous-quadrants
        for p in self.particles:
            self.northwest.insert(p)
            self.northeast.insert(p)
            self.southwest.insert(p)
            self.southeast.insert(p)

        self.particles = []
        self.divided = True

    def query(self, range_rect, found=None):
        if found is None:
            found = []

        # Si la zone de recherche n'intersecte pas ce quadrant, retourner vide
        if not self.boundary.intersects(range_rect):
            return found

        # Vérifier les particules ou triangles dans ce quadrant
        for item in self.particles:
            # Si c'est une particule
            if hasattr(item, 'form'):
                if range_rect.contains(item.form.center):
                    found.append(item)
            # Si c'est un triangle
            elif hasattr(item, 'bounding_rect'):
                if item.bounding_rect.intersects(range_rect):
                    found.append(item)

        # Vérifier les sous-quadrants si divisé
        if self.divided:
            self.northwest.query(range_rect, found)
            self.northeast.query(range_rect, found)
            self.southwest.query(range_rect, found)
            self.southeast.query(range_rect, found)

        return found

    def clear(self):
        self.particles = []
        if self.divided:
            self.northwest = None
            self.northeast = None
            self.southwest = None
            self.southeast = None
            self.divided = False