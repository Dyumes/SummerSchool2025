import random
import pygame
#from Demos.win32console_demo import window_size
from pygame import gfxdraw
import pyautogui
import math
import numpy as np
from sympy.logic.inference import valid
from win32api import GetSystemMetrics
from Particles import Environment, Force, Vector

#TODO : PALM TREE, FILL EMPTY ZONE WITH A FLAT SQUARE, SUN SCALING

pygame.init()

windowWidth = pyautogui.size()[0] - 100
windowHeight = pyautogui.size()[1] - 100
print(f"pyautogui : {windowWidth} - {windowHeight}\nautre : {pyautogui.size()[0]} - {pyautogui.size()[1]}")
WINDOW_SIZE = (windowWidth, windowHeight)
#Display pygame with a bit smaller resolution than the screen itself no matter the os
window = pygame.display.set_mode((windowWidth, windowHeight))

fps = 60
clock = pygame.time.Clock()
dt = clock.tick(fps) / 1000

NBR_TRIANGLE_IN_CIRCLE = 8
CIRCLE_RADIUS = 10
SUN_PARTICLE_RADIUS = 5
PARTICLE_COLOR = (255, 100, 0)
SUN_PARTICLE_COLOR = (255, 255, 0)
SUN_PARTICLE_COLOR_DELTA = 150
MIN_PARTICLES = 300
MAX_PARTICLES = 300
GRAVITY_MAGNITUDE = 9.81
GRAVITY_DIRECTION = math.pi / 2
HANDLING_PARTICLES_COLLISIONS = False
HANDLING_OBJECTS_COLLISIONS = False
HANDLING_SUN_COLLISIONS = True
SUN_GRAVITY_MAGNITUDE = 1

# suns = []
#mountains = []
cubes = []
palms = []
grounds = []
validGround = []


# Old sun generation
"""
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
            self.offset += 1 * bpm/60
            if self.offset >= 60:
                self.offset = 60
                self.maxReached = True
        else:
            self.offset -= 1 * bpm/60
            if self.offset <= 0:
                self.offset = 0
                self.maxReached = False

        if self.previous_offset == self.offset:
            self.is_static = True
        else:
            self.is_static = False


    def draw(self):
        for t in range(self.nbrTriangle):
            angle1 = (2*math.pi*t) / self.nbrTriangle
            angle2 = (2*math.pi*(t+1)) / self.nbrTriangle
            midAngle = (angle1 + angle2)/2

            endCenterX = self.centerX + (( self.offset) * math.cos(midAngle))
            endCenterY = self.centerY + ((self.offset) * math.sin(midAngle))

            x1 = endCenterX + ((self.radius + self.offset) * math.cos(angle1))
            y1 = endCenterY + ((self.radius + self.offset) * math.sin(angle1))
            x2 = endCenterX + ((self.radius + self.offset) * math.cos(angle2))
            y2 = endCenterY + ((self.radius + self.offset) * math.sin(angle2))

            pygame.draw.polygon(window, (255, 100, 0), [[self.centerX, self.centerY],
                                                        [self.centerX + ((self.radius + self.offset) * math.cos(angle1)),
                                                         self.centerY + ((self.radius + self.offset) * math.sin(angle1))],
                                                        [self.centerX + ((self.radius + self.offset) * math.cos(angle2)),
                                                         self.centerY + ((self.radius + self.offset) * math.sin(angle2))]])

            pygame.draw.polygon(window, (255, 167, 0), [[self.centerX, self.centerY], [x1, y1], [x2, y2]])

            pygame.draw.polygon(window, (255, 255, 0), [
                [endCenterX, endCenterY], [x1, y1], [x2, y2]
            ])
"""

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

#Old mountain generation
"""
class Mountain:
    def __init__(self, position):
        self.position = position
        self.growthSpeed = 500
        self.height = 0
        self.maxHeight = 200
        self.animationTime = 1
        self.maxReached = False
        self.triangles = []
        self.canMove = False
        self.startTime = 0


    def update(self, time):
        animationCurrentTime = time - self.startTime
        if self.canMove:
            if animationCurrentTime >= self.animationTime:
                self.height = 0
            elif  animationCurrentTime < 0.2 * self.animationTime:
                self.height = self.maxHeight / (0.2 * self.animationTime) * animationCurrentTime
            elif animationCurrentTime > 0.6 * self.animationTime:
                self.height = self.maxHeight / (0.6 * self.animationTime - self.animationTime) * animationCurrentTime + (self.maxHeight / 0.4)
            else:
                self.height = self.maxHeight * 0.1 * math.sin(animationCurrentTime * 20) + self.maxHeight
            # if not self.maxReached:
            #     self.height += self.growthSpeed * dt
            #     if self.height >= self.maxHeight:
            #         self.height = self.maxHeight
            #         self.maxReached = True
            # else:
            #     self.height -= self.growthSpeed * dt
            #     if self.height <= 0:
            #         self.height = 0
            #         self.canMove = False
            #         self.maxReached = False


    def createMountain(self):
        nbrTriangle = 10
        intBlue = 100
        baseY = self.position[1]
        width = (windowWidth) / 12

        # First triangle to display (basis)
        p1 = (self.position[0], baseY)
        p2 = (self.position[0] + width, baseY)

        # Triangle width
        tri_width = p2[0] - p1[0]

        min_x = int(p1[0] + tri_width * 0.1)
        max_x = int(p1[0] + tri_width * 0.9)
        topX = random.randrange(min_x, max_x)

        # Peak variation
        topY = baseY - self.height
        p3 = (topX, topY)

        first_tri = Triangle((0, 0, intBlue), p1, p2, p3)
        self.triangles.append(first_tri)

        # Set the free sides for the next triangle - ON ENLÈVE LA BASE!
        freeSides = [(p1, p3), (p2, p3)]  # Seulement les côtés, pas la base

        # Add more triangles
        for i in range(nbrTriangle):
            if not freeSides:
                break
            side = freeSides.pop(0)
            (a, b) = side

            # Create a new peak
            midX = (a[0] + b[0]) / 2
            midY = (a[1] + b[1]) / 2
            a = (a[0], a[1] - self.height)
            b = (b[0], b[1] - self.height)
            b = (b[0], b[1] - self.height)
            height = random.randrange(40, 120)
            p_new = (midX, midY - height)

            intBlue += int(155 / nbrTriangle)
            tri = Triangle(
                (0, 0, intBlue),
                a, b, p_new
            )
            self.triangles.append(tri)

            # new sides to add except the one that is shared
            freeSides.append((a, p_new))
            freeSides.append((b, p_new))


    def draw(self):
        for i, tri in enumerate(self.triangles):
            color = tri.get_color()
            if i == 0:
                pygame.draw.polygon(window, color, [(tri.p1[0], tri.p1[1]),(tri.p2[0], tri.p2[1]), (tri.p3[0], tri.p3[1] - self.height)])
            else :
                pygame.draw.polygon(window, color, [(tri.p1[0], tri.p1[1]),(tri.p2[0], tri.p2[1] - self.height), (tri.p3[0], tri.p3[1] - self.height)])
            # For debug if necessary
            #pygame.draw.circle(window, (255, 0, 0), (tri.p1[0], tri.p1[1]), 5)
            #pygame.draw.circle(window, (0, 255, 0), (tri.p2[0], tri.p2[1]), 3)
            #pygame.draw.circle(window, (0, 255, 255), (tri.p3[0], tri.p3[1] - self.height), 5)

"""

def violet_gradient_color(depth, min_depth=600, max_depth=1100):
    t = (depth - min_depth) / (max_depth - min_depth)
    t = np.clip(t, 0, 1)
    dark_violet = np.array([90, 40, 120])
    mid_violet  = np.array([170, 40, 165])
    light_violet = np.array([220, 180, 255])
    if t < 0.5:
        color = dark_violet * (1 - t*2) + mid_violet * (t*2)
    else:
        color = mid_violet * (1 - (t-0.5)*2) + light_violet * ((t-0.5)*2)
    return tuple(int(c) for c in color)

class Cube:
    def __init__(self, triangle1:Triangle, triangle2:Triangle):
        self.triangle1 = triangle1
        self.triangle2 = triangle2
        self.p1 = triangle1.get_position1()
        self.p2 = triangle1.get_position2()
        self.p3 = triangle1.get_position3()
        self.p4 = triangle2.get_position3()
        self.baseColor = self.getBaseColor()
        self.speed = 10
        self.height = 0
        self.maxHeight = 50
        self.animationTime = 1
        self.maxReached = False
        self.offset = random.randrange(0, 1000)
        self.isValid = False
        self.canMove = False
        self.startTime = 0
        self.neighbors = []
        self.wave_active = False
        self.wave_start_time = 0
        self.wave_delay = 0


    def trigger_wave(self, time, delay=0):
        self.wave_active = True
        self.wave_start_time = time
        self.wave_delay = delay
        self.canMove = True

        for neighbor in self.neighbors:
            if not neighbor.wave_active:
                neighbor.trigger_wave(time, delay + 0.1)

    def getBaseColor(self):
        depth = self.get_depth()
        return violet_gradient_color(depth)

        #return [int(c) for c in color]

    def changeColor(self, color):
        self.baseColor = list(color)


    def update(self, time):
        if self.wave_active:
            elapsed = (time - self.wave_start_time) / 1000 - self.wave_delay

            if elapsed >= 0:
                self.height = 2 * self.maxHeight * math.sin(elapsed * 5) * math.exp(-elapsed * 2)

                if elapsed > 2:
                    self.wave_active = False
                    self.canMove = False
                    self.height = 0
        """
        animationCurrentTime = time - self.startTime
        if self.canMove and self.isValid:
            if  animationCurrentTime < 0.2 * self.animationTime:
                self.height = (0.2 * self.animationTime) / self.maxHeight * animationCurrentTime
            elif animationCurrentTime > 0.8 * self.animationTime:
                self.height = 1 * (0.2 * self.animationTime) / self.maxHeight * animationCurrentTime
            else:
                self.height = -self.maxHeight * 0.1 * math.sin(animationCurrentTime * 20) + self.maxHeight
        """
    def draw(self):
        p1 = self.p1
        p2 = self.p2
        p3 = self.p3
        p4 = self.p4



        if p1[1] <= pyautogui.size()[1]/2  or p2[0] > pyautogui.size()[0] or p1[0] < 0:
            self.isValid = False
        else:
            self.isValid = True
            p1h = (p1[0], p1[1] - self.height)
            p2h = (p2[0], p2[1] - self.height)
            p3h = (p3[0], p3[1] - self.height)
            p4h = (p4[0], p4[1] - self.height)


            if p1[1] > pyautogui.size()[1]/2:
                # right
                pygame.draw.polygon(window, self.baseColor, [p2, p3, p3h])
                pygame.draw.polygon(window, self.baseColor, [p2, p3h, p2h])
                
                # left
                left_color = [min(c+40,255) for c in self.baseColor]
                pygame.draw.polygon(window, left_color, [p4, p1, p1h])
                pygame.draw.polygon(window, left_color, [p4, p1h, p4h])
                
                # front
                front_color = [min(c+20,255) for c in self.baseColor]
                pygame.draw.polygon(window, front_color, [p1, p2, p2h])
                pygame.draw.polygon(window, front_color, [p1, p2h, p1h])
                
                # top
                top_color = [min(c+80,255) for c in self.baseColor]
                pygame.draw.polygon(window, top_color, [p1h, p2h, p3h])
                pygame.draw.polygon(window, top_color, [p1h, p3h, p4h])
                """
            else:
                # right
                pygame.draw.polygon(window, (self.baseColor[0], self.baseColor[1], self.baseColor[2]), [p2, p3, p3h])
                pygame.draw.polygon(window, (self.baseColor[0], self.baseColor[1], self.baseColor[2]), [p2, p3h, p2h])

            # top
            pygame.draw.polygon(window, (self.baseColor[0] + 80, self.baseColor[1], self.baseColor[2] + 80), [p1h, p2h, p3h])
            pygame.draw.polygon(window, (self.baseColor[0] + 80, self.baseColor[1], self.baseColor[2] + 80), [p1h, p3h, p4h])
            """""

    def linear_interpolation_color(self,color1, color2, factor):
        color = (int(color1[0] + (color2[0] - color1[0])*factor),
                 int(color1[1] + (color2[1] - color1[1])*factor),
                 int(color1[2] + (color2[2] - color1[2])*factor))

        return color

    def get_depth(self):
        return (self.p1[1] + self.p2[1] + self.p3[1] + self.p4[1]) / 4

    def get_xmean(self):
        return (self.p1[0] + self.p2[0] + self.p3[0] + self.p4[0]) / 4

def find_neighbors():
    for cube in validGround:
        cube.neighbors = []

        left = validGround.index(cube) - 1
        if left >= 72 or left % 12 < 1:
            pass
        else:
            cube.neighbors.append(validGround[left])
        right = validGround.index(cube) + 1
        if right >= 72 or right%12 < 1:
            pass
        else:
            cube.neighbors.append(validGround[right])


    """
    for cube in validGround:
        cube.neighbors = []

        left = validGround.index(cube) - 1
        if left >= 72 or left % 12 < 1:
            pass
        else:
            cube.neighbors.append(validGround[left])
        right = validGround.index(cube) + 1
        if right >= 72 or right%12 < 1:
            pass
        else:
            cube.neighbors.append(validGround[right])

        
        bottom = validGround.index(cube) - 12
        if bottom >= 72 or bottom % 12  < 1:
            pass
        else:
            cube.neighbors.append(validGround[bottom])

     Changement algo 
    for i, cube in enumerate(validGround):
        x_mean = cube.get_xmean()
        y_mean = cube.get_depth()

        for other in validGround:
            if cube != other:
                other_x = other.get_xmean()
                other_y = other.get_depth()

                distance = math.sqrt((x_mean - other_x)**2 + (y_mean - other_y)**2)
                if distance < 100:
                    cube.neighbors.append(other)
    """
def get_transformation(src, dst):
    A = []
    for (x,y), (X,Y) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -X*x, -X*y, -X])
        A.append([0, 0, 0, x, y, 1, -Y*x, -Y*y, -Y])
    A = np.array(A, dtype=float)

    U,S,Vt = np.linalg.svd(A)
    H = Vt[-1].reshape((3,3))
    return H / H[2,2]  #normalization

def apply_transformation(pt, H):
    x,y = pt
    vec = np.array([x,y,1.0])
    res = H.dot(vec)
    return (res[0]/res[2], res[1]/res[2])

#TODO : Do it window scaled
class Ground():
    def __init__(self):
        self.cols = 12*6
        self.rows = 9*3
        self.triangles = []

    def groundGeneration(self):
        cell_width = 50
        cell_height = cell_width

        W = self.cols*cell_width
        H = self.rows*cell_height

        src = [(0, 0), (W, 0), (W, H), (0,H)]

        base_y = pyautogui.size()[1]
        dest = [
            (pyautogui.size()[0]/2-(pyautogui.size()[0]*4)-50, base_y),
            (pyautogui.size()[0]/2+(pyautogui.size()[0]*4)-50, base_y),
            (pyautogui.size()[0] -50 -pyautogui.size()[0]/5, (windowHeight) *7/16 ),
            (-50 +pyautogui.size()[0]/5, (windowHeight) * 7/16)
        ]

        transfo = get_transformation(src, dest)

        for i in range(self.rows):
            for j in range(self.cols):
                p1 = (j*cell_width, i*cell_height)
                p2 = ((j + 1) * cell_width, i * cell_height)
                p3 = ((j + 1) * cell_width, (i + 1) * cell_height)
                p4 = ((j * cell_width), (i + 1)* cell_height)

                P1 = apply_transformation(p1, transfo)
                P2 = apply_transformation(p2, transfo)
                P3 = apply_transformation(p3, transfo)
                P4 = apply_transformation(p4, transfo)

                if P1[1] > pyautogui.size()[1]/2 + 10 and P1[0] > 0 and P2[0] < windowWidth:
                    color = (127,0,255)
                    t1 = Triangle(color, (int(P1[0]),int(P1[1])), (int(P2[0]),int(P2[1])), (int(P3[0]),int(P3[1])) )
                    t2 = Triangle(color, (int(P1[0]),int(P1[1])), (int(P3[0]),int(P3[1])), (int(P4[0]),int(P4[1])) )
                    self.triangles.append(t1)
                    self.triangles.append(t2)

                    cube = Cube(t1, t2)
                    cubes.append(cube)


    def draw(self):
        #TODO : VOIR POUR LES COULEURS ET EFFET DE PROFONDEUR
        for tri in reversed(self.triangles):
            color = tri.get_color()
            pygame.gfxdraw.trigon(window, tri.p1[0], tri.p1[1],tri.p2[0], tri.p2[1], tri.p3[0], tri.p3[1],color)

        pygame.draw.polygon(window, (170, 40, 165),
                            [(0,int(pyautogui.size()[1]/2)),
                             (0, int(pyautogui.size()[1])),
                             (int(pyautogui.size()[0]), int(pyautogui.size()[1]/2))])
        pygame.draw.polygon(window, (170, 40, 165),
                        [(int(pyautogui.size()[0]),int(pyautogui.size()[1])),
                         (0, int(pyautogui.size()[1])),
                         (int(pyautogui.size()[0]), int(pyautogui.size()[1]/2))])
        for cube in validGround:
            if validGround.index(cube) % 12 == 0:
                depth = cube.get_depth()
                color = violet_gradient_color(depth)
                p1 = cube.p1
                p2 = cube.p2
                p3 = cube.p3
                p4 = cube.p4
                print("p1:", p1, "p2:", p2, "p3:", p3, "p4:", p4)
                pygame.draw.polygon(window, color, [(0, p1[1]), (0, p3[1]),(windowWidth, p4[1])])
                pygame.draw.polygon(window, color, [(0, p1[1]), (windowWidth, p3[1]),(windowWidth, p2[1])])

    #draw a rectangle for hiding extended triangles going beyond mountains
    def gradientHiding(self):

        """
        pygame.draw.polygon(window,
                            (0, 0, 0),
                            ((0, 0),
                             (0, (windowHeight) / 2),
                             (pyautogui.size()[0], (windowHeight) / 2))
                            )
        pygame.draw.polygon(window,
                            (0, 0, 0),
                            ((0, 0),
                             (pyautogui.size()[0], 0),
                             (pyautogui.size()[0],(windowHeight) / 2))
                            )
        """
    def clear(self):
        self.triangles = []


class Palm:
    def __init__(self):
        self.triangles = []
        self.DARK_BROWN = (101, 67, 33)
        self.LIGHT_BROWN = (205, 133, 63)
        self.DARK_GREEN = (0, 100, 0)
        self.GREEN = (34, 139, 34)
        self.LIGHT_GREEN = (144, 238, 144)

    def createGradientRectangleTriangles(self, x, y, width, height, angle, color1, color2):
        halfWidth = width / 2
        halfHeight = height / 2

        # rectangle debout (hauteur dans l'axe Y)
        points = [
            (-halfWidth, 0),
            (halfWidth, 0),
            (halfWidth, height),
            (-halfWidth, height)
        ]

        angleRad = math.radians(angle)
        rotatedPoints = []
        for px, py in points:
            rx = px * math.cos(angleRad) - py * math.sin(angleRad)
            ry = px * math.sin(angleRad) + py * math.cos(angleRad)
            rotatedPoints.append((x + rx, y + ry))

        # 2 triangles pour former le rectangle
        t1 = Triangle(color1, rotatedPoints[0], rotatedPoints[1], rotatedPoints[2])
        t2 = Triangle(color2, rotatedPoints[0], rotatedPoints[2], rotatedPoints[3])
        return [t1, t2]


    def generatePalm(self, x, y, depth, maxDepth, width, angle):
        triangles = []
        length = 100

        # on trace un segment dans la direction "angle"
        endX = x + length * math.cos(math.radians(angle))
        endY = y + length * math.sin(math.radians(angle))

        segmentTriangles = self.createGradientRectangleTriangles(
            (x + endX) / 2,
            (y + endY) / 2,
            width,
            length,
            angle,   # <== correction : on passe l'angle courant
            self.DARK_BROWN,
            self.LIGHT_BROWN
        )
        triangles.extend(segmentTriangles)

        new_width = width * 0.7

        # on génère les branches
        if depth < maxDepth:
            numBranches = random.randint(2, 3)
            for _ in range(numBranches):
                newAngle = angle + random.uniform(-30, 30)
                branchTriangles = self.generatePalm(endX, endY, depth + 1, maxDepth, new_width, newAngle)
                triangles.extend(branchTriangles)

        # si on est en bout de tronc -> feuilles
        if depth >= maxDepth - 1:
            leafCount = random.randint(3, 6)
            for _ in range(leafCount):
                leafSize = length * random.uniform(0.8, 1.5)
                leafAngle = random.uniform(0, 360)
                leafDistance = random.uniform(0.5, 1.0)

                leafX = endX + (length * leafDistance) * math.cos(math.radians(angle))
                leafY = endY + (length * leafDistance) * math.sin(math.radians(angle))

                leafPoints = [
                    (leafX, leafY),
                    (leafX + leafSize * math.cos(math.radians(leafAngle)),
                     leafY + leafSize * math.sin(math.radians(leafAngle))),
                    (leafX + leafSize * math.cos(math.radians(leafAngle + 120)),
                     leafY + leafSize * math.sin(math.radians(leafAngle + 120)))
                ]

                leafColor = random.choice([self.DARK_GREEN, self.GREEN, self.LIGHT_GREEN])
                triangles.append(Triangle(leafColor, leafPoints[0], leafPoints[1], leafPoints[2]))

        return triangles

    def draw(self):
        for triangle in self.triangles:
            pygame.draw.polygon(window,
                                triangle.get_color(),
                                (triangle.p1, triangle.p2, triangle.p3))

    def clear(self):
        self.triangles.clear()

"""
def spawnMountains():
    positionX = 0
    positionY = (pyautogui.size()[1]) / 2

    for m in range(12):
        mountain = Mountain((positionX, positionY))
        mountains.append(mountain)
        mountain.createMountain()

        positionX += (windowWidth) / 12
"""
firstLaunch = True
#s1 = Sun((windowWidth) / 2, (windowHeight)/ 2 - (pyautogui.size()[1]/4), 16, 100)
#s1 = Sun((windowWidth) / 2, (windowHeight)/ 2 - (GetSystemMetrics(1)/4), 16, 100)
g = Ground()
p1 = Palm()

# Sort by depth and side
def getSortKey(cube):
    depth = cube.get_depth()
    x_mean = cube.get_xmean()
    if x_mean < pyautogui.size()[0] / 2:
        return (depth, x_mean)   # left side : left to right
    else:
        return (depth, -x_mean)  # right side : right to left


#only for debug
#font = pygame.font.Font('freesansbold.ttf', 32)


def globalGeneration(time, bpm):
    #global s1
    if firstLaunch:
        # spawnMountain()
        #s1 = Sun((windowWidth) / 2, (windowHeight)/ 2 - (pyautogui.size()[1]/4), 16, 100)
        #suns.append(s1)
        #s1 = Sun((windowWidth) / 2, (windowHeight)/ 2 - (GetSystemMetrics(1)/4), 16, 100)
        #suns.append(s1)
        #spawnMountains()
        g.groundGeneration()
        generateValidGround()
        assignCubesToColumns()
        printCubesPerColumn()
        grounds.append(g)
        #playTrumpet(1)
        p1.generatePalm(windowWidth / 2, windowHeight / 2, 0, 5, 50, 90)
        palms.append(p1)
    elif not firstLaunch:
        g.draw()
        #for sun in suns:
        #    sun.draw()
        #    sun.update(bpm)

        # env_with_sun.draw()
        # env_with_sun.update()
        #
        # # Commented out for the presentation because of bugs
        # env_objects = mountains
        # for mountain in mountains: print(mountain)
        # env.draw()
        # env.update(env_objects)

        # for mountain in mountains:
        #     mountain.draw()
        #     if mountain.canMove:
        #         mountain.update(time)
        #s1.draw()
        #s1.update(bpm)
        # for mountain in mountains:
        #     mountain.draw()
        #     if mountain.canMove:
        #         mountain.update(time)


        cubes_sorted = sorted(validGround, key=getSortKey)
        timeAnimation = 0
        for cube in cubes_sorted:
            cube.update(pygame.time.get_ticks())
            cube.draw()
        pygame.draw.polygon(window, (255, 255, 255),
                                [(0, windowHeight), (0, validGround[0].p1[1]), (windowWidth, validGround[0].p2[1])])
        pygame.draw.polygon(window, (255, 255, 255),
                        [(0, windowHeight), (windowWidth, windowHeight), (windowWidth, validGround[0].p1[1])])
        # text = font.render('GeeksForGeeks', True, (125, 125, 125), (125, 0, 125))
        # window.blit(text, (cube.get_xmean, cube.get_depth))

        for palm in palms:
            palm.draw()


"""
def clearAll():
    global mountains
    global cubes
    suns.clear()
    mountains.clear()
    cubes.clear()
    palms.clear()
    grounds.clear()
"""

font = pygame.font.SysFont("Arial", 30)
def fps_counter(win, clk):
    fps = str(int(clk.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    win.blit(fps_t,(0,0))

"""
def playTrumpet(nbr):
    mountains[nbr].canMove = True
    # if mountains[nbr].canMove:
    #     mountains[nbr].canMove = False
    # else:
    #     mountains[nbr].canMove = True
"""

notes = []
for i in range(12):
    notes.append((i,(14 *(i + 1), 0, 14 * (i + 1))))

def generateValidGround():
    for cube in cubes:
        if 7 < cubes.index(cube) < 20 or 21 < cubes.index(cube) < 34 or 39 < cubes.index(cube) < 52 or 61 < cubes.index(cube) < 74 or 87 < cubes.index(cube) < 100 or 117 < cubes.index(cube) < 130:
            validGround.append(cube)
        else:
            pass
    find_neighbors()

cubes_by_column = [[] for _ in range(12)]

def assignCubesToColumns():
    global cubes_by_column
    cubes_by_column = [[] for _ in range(12)]

    for i, cube in enumerate(validGround):
        col = i // 6
        col = min(col, 11)
        cubes_by_column[col].append(cube)

def trigger_all_cubes_wave():
    current_time = pygame.time.get_ticks()
    delay_between = 500
    for i, cube in enumerate(validGround):
        if cube.isValid:
            cube.trigger_wave(current_time, delay=i*delay_between/1000)






def printCubesPerColumn():
    counter = 0
    for i in cubes_by_column:
        for j in i:
            print("Cube - ", end='')
            counter += 1
        print(";")
    print(f"nbr of cubes : {counter}")

allMoving = False
def playPiano(note):
    global allMoving

    if not cubes_by_column[note]:
        return

    available_cubes = [c for c in cubes_by_column[note] if not c.wave_active]

    if not available_cubes:
        return

    cube = random.choice(available_cubes)
    cube.changeColor(notes[note][1])

    current_time = pygame.time.get_ticks()
    cube.trigger_wave(current_time)



def playPianoAll():
    for cube in validGround:
        if cube.canMove:
            cube.height = 0
            cube.changeColor((cube.getBaseColor()[0], cube.getBaseColor()[1], cube.getBaseColor()[2]))
            cube.canMove = False
        else :
            cube.canMove = True


# Not used
"""
def changeMountainGrowthSpeed(newSpeed, nbr):
    mountains[nbr].growthSpeed = newSpeed

def changeMountainMaxHeight(newHeight, nbr):
    mountains[nbr].maxHeight = newHeight

def changeMountainAnimiationTime(newAnimiationTime, nbr):
    mountains[nbr].animationTime = newAnimiationTime

def changeMountainStartTime(newStartTime, nbr):
    mountains[nbr].startTime = newStartTime
"""

def changeCubeGrowthSpeed(newSpeed, nbr):
    cubes[nbr].growthSpeed = newSpeed

def changeCubeMaxHeight(newHeight, nbr):
    cubes[nbr].maxHeight = newHeight

def changeCubeAnimiationTime(newAnimiationTime, nbr):
    cubes[nbr].animationTime = newAnimiationTime

def changeCubeStartTime(newStartTime, nbr):
    cubes[nbr].startTime = newStartTime

# env_with_sun = Environment(WINDOW_SIZE)
# env_with_sun.handling_sun_collisions = True
# env_with_sun.handling_objects_collisions = False
# env_with_sun.handling_particles_collisions = False
# env_with_sun.min_particles = 100
# env_with_sun.max_particles = 100
#
# env = Environment(WINDOW_SIZE)
# env.handling_sun_collisions = False
# env.handling_objects_collisions = True
# env.handling_particles_collisions = False
# env.min_particles = 10
# env.max_particles = 10
#
# gravity = Force(Vector(GRAVITY_MAGNITUDE, GRAVITY_DIRECTION))
#
# env_with_sun.sun = s1
#
# for _ in range(random.randint(env_with_sun.min_particles, env_with_sun.max_particles)):
#     env_with_sun.create_particle_around_sun(s1)
#
# for _ in range(random.randint(env.min_particles, env.max_particles)):
#     env.create_particle()
#
# for particle in env.particles:
#     particle.add_force(gravity)


if __name__ == "__main__":

    running = True

    while running:

        #window.fill((0, 0, 0))

        globalGeneration(clock.tick(), 60)
        firstLaunch = False
        fps_counter(window, clock)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                quit()

            if event.type == pygame.KEYDOWN:
                match event.key :
                    case pygame.K_r:
                        window.fill((0, 0, 0))
                        #clearAll()
                        firstLaunch = True
                    case pygame.K_1:
                        #playTrumpet(1)
                        note = random.randint(8, 9)
                        print(f"note : {note}")
                        playPiano(note)

                    case pygame.K_2:
                        playPianoAll()
                    #test, make every cube waving in the right order
                    case pygame.K_4:
                        trigger_all_cubes_wave()



        clock.tick(fps)


        pygame.display.update()
