import pygame
from pygame import gfxdraw
import math
import numpy as np
import array as ar
from random import randrange
import pygame_widgets
from fontTools.ttLib.tables.C_P_A_L_ import Color
from pygame_widgets.textbox import TextBox
from matplotlib.widgets import Slider
from sympy.core.random import random
from win32api import GetSystemMetrics

#TODO : TREES, PLAY INSTRUMENT WITH CUBE GROWING/ACTIVE CUBE, FILL EMPTY ZONE WITH A FLAT SQUARE

pygame.init()


#Display pygame with a bit smaller resolution than the screen itself no matter the os
window = pygame.display.set_mode((GetSystemMetrics(0) - 100, GetSystemMetrics(1) - 100))

fps = 60
clock = pygame.time.Clock()
dt = clock.tick(fps) / 1000

mountains = []

squares = []

class Sun:
    def __init__(self, centerX, centerY, nbrTriangle, radius):
        self.nbrTriangle = nbrTriangle
        self.radius = radius
        self.centerX = centerX
        self.centerY = centerY
        self.offset = 0
        self.maxReached = False

    def update(self):
        if not self.maxReached:
            self.offset += 1
            if self.offset >= 50:
                self.offset = 50
                self.maxReached = True
        else:
            self.offset -= 1
            if self.offset <= 0:
                self.offset = 0
                self.maxReached = False


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
            if  animationCurrentTime < 0.2 * self.animationTime:
                self.height = (0.2 * self.animationTime) / self.maxHeight * animationCurrentTime
            elif animationCurrentTime > 0.8 * self.animationTime:
                self.height = -1 * (0.2 * self.animationTime) / self.maxHeight * animationCurrentTime
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
        nbrTriangle = 5
        intBlue = 100
        baseY = self.position[1]
        width = (GetSystemMetrics(0) - 100) / 12

        # First triangle to display (basis)
        p1 = (self.position[0], baseY)
        p2 = (self.position[0] + width, baseY)

        # Triangle width
        tri_width = p2[0] - p1[0]

        min_x = int(p1[0] + tri_width * 0.1)
        max_x = int(p1[0] + tri_width * 0.9)
        topX = randrange(min_x, max_x)

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
            height = randrange(40, 120)
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

class Square:
    def __init__(self, triangle1:Triangle, triangle2:Triangle):
        self.triangle1 = triangle1
        self.triangle2 = triangle2
        self.p1 = triangle1.get_position1()
        self.p2 = triangle1.get_position2()
        self.p3 = triangle1.get_position3()
        self.p4 = triangle2.get_position3()
        self.height = 0
        self.speed = 2
        self.offset = randrange(0, 1000)
        self.isValid = False
        self.canMove = True

    def update(self, time):
        if self.canMove and self.isValid:
            self.height = 30 * math.sin((time + self.offset) * 0.005) + 30

    def draw(self):
        p1 = self.p1
        p2 = self.p2
        p3 = self.p3
        p4 = self.p4

        if p1[1] <= GetSystemMetrics(1)/2  or p2[0] > GetSystemMetrics(0) or p1[0] < 0:
            self.isValid = False
        else:
            self.isValid = True
            p1h = (p1[0], p1[1] - self.height)
            p2h = (p2[0], p2[1] - self.height)
            p3h = (p3[0], p3[1] - self.height)
            p4h = (p4[0], p4[1] - self.height)

            if p1[1] > GetSystemMetrics(1)/2:

                # right
                pygame.draw.polygon(window, (120, 0, 120), [p2, p3, p3h])
                pygame.draw.polygon(window, (120, 0, 120), [p2, p3h, p2h])

                # left
                pygame.draw.polygon(window, (170, 0, 170), [p4, p1, p1h])
                pygame.draw.polygon(window, (170, 0, 170), [p4, p1h, p4h])

                # front
                pygame.draw.polygon(window, (150, 0, 150), [p1, p2, p2h])
                pygame.draw.polygon(window, (150, 0, 150), [p1, p2h, p1h])

            else:
                # right
                pygame.draw.polygon(window, (120, 0, 120), [p2, p3, p3h])
                pygame.draw.polygon(window, (120, 0, 120), [p2, p3h, p2h])

            # top
            pygame.draw.polygon(window, (200, 0, 200), [p1h, p2h, p3h])
            pygame.draw.polygon(window, (200, 0, 200), [p1h, p3h, p4h])


    def get_depth(self):
        return (self.p1[1] + self.p2[1] + self.p3[1] + self.p4[1]) / 4

    def get_xmean(self):
        return (self.p1[0] + self.p2[0] + self.p3[0] + self.p4[0]) / 4


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

        base_y = GetSystemMetrics(1)
        dest = [
            (GetSystemMetrics(0)/2-(GetSystemMetrics(0)*4)-50, base_y),
            (GetSystemMetrics(0)/2+(GetSystemMetrics(0)*4)-50, base_y),
            (GetSystemMetrics(0) -50 -GetSystemMetrics(0)/5, (GetSystemMetrics(1) - 100) *7/16 ),
            (-50 +GetSystemMetrics(0)/5, (GetSystemMetrics(1) - 100) *7/16)
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

                if P1[1] > GetSystemMetrics(1)/2:
                    color = (127,0,255)
                    t1 = Triangle(color, (int(P1[0]),int(P1[1])), (int(P2[0]),int(P2[1])), (int(P3[0]),int(P3[1])) )
                    t2 = Triangle(color, (int(P1[0]),int(P1[1])), (int(P3[0]),int(P3[1])), (int(P4[0]),int(P4[1])) )
                    self.triangles.append(t1)
                    self.triangles.append(t2)

                    square = Square(t1, t2)
                    squares.append(square)



    def draw(self):
        for tri in reversed(self.triangles):
            color = tri.get_color()
            pygame.gfxdraw.trigon(window, tri.p1[0], tri.p1[1],tri.p2[0], tri.p2[1], tri.p3[0], tri.p3[1],color)

            #draw a rectangle for hiding extended triangles going beyond mountains
        pygame.draw.polygon(window,
                            (0, 0, 0),
                            ((0, 0),
                             (0, (GetSystemMetrics(1) - 100) / 2),
                             (GetSystemMetrics(0), (GetSystemMetrics(1) - 100) / 2))
                            )
        pygame.draw.polygon(window,
                            (0, 0, 0),
                            ((0, 0),
                             (GetSystemMetrics(0), 0),
                             (GetSystemMetrics(0),(GetSystemMetrics(1) - 100) / 2))
                            )

    def clear(self):
        self.triangles = []

def spawnMountains():
    positionX = 0
    positionY = (GetSystemMetrics(1)) / 2

    for m in range(12):
        mountain = Mountain((positionX, positionY))
        mountains.append(mountain)
        mountain.createMountain()

        positionX += (GetSystemMetrics(0) - 100) / 12

firstLaunch = True
s1 = Sun((GetSystemMetrics(0) - 100) / 2, (GetSystemMetrics(1) - 100)/ 2 - (GetSystemMetrics(1)/4), 16, 100)
g = Ground()

# Sort by deepness and side
def getSortKey(square):
    depth = square.get_depth()
    x_mean = square.get_xmean()
    if x_mean < GetSystemMetrics(0) / 2:
        return (depth, x_mean)   # left side : left to right
    else:
        return (depth, -x_mean)  # right side : right to left

def globalGeneration(time):
    if firstLaunch:
        spawnMountains()
        g.groundGeneration()
        #playTrumpet(1)
    elif not firstLaunch:
        g.draw()
        s1.draw()
        s1.update()
        for mountain in mountains:
            mountain.draw()
            if mountain.canMove:
                mountain.update(time)

        squares_sorted = sorted(squares, key=getSortKey)
        for square in squares_sorted:
            square.update(pygame.time.get_ticks())
            square.draw()


def clearAll():
    global mountains
    global squares
    mountains.clear()
    squares.clear()
    g.clear()


font = pygame.font.SysFont("Arial", 30)
def fps_counter(win, clk):
    fps = str(int(clk.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    win.blit(fps_t,(0,0))

def playTrumpet(nbr): #TODO : SEE IF WE RECEIVE THE NOTE NAME OR THE PLACE
    mountains[nbr].canMove = True
    # if mountains[nbr].canMove:
    #     mountains[nbr].canMove = False
    # else:
    #     mountains[nbr].canMove = True

def playPiano(nbr):
    squares.canmove = True

def changeMountainGrowthSpeed(newSpeed, nbr):
    mountains[nbr].growthSpeed = newSpeed

def changeMountainMaxHeight(newHeight, nbr):
    mountains[nbr].maxHeight = newHeight

def changeMountainAnimiationTime(newAnimiationTime, nbr):
    mountains[nbr].animationTime = newAnimiationTime

def changeMountainStartTime(newStartTime, nbr):
    mountains[nbr].startTime = newStartTime

if __name__ == "__main__":

    running = True


    while running:

        window.fill((0, 0, 0))

        globalGeneration(clock.tick())
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
                        clearAll()
                        firstLaunch = True
                    case pygame.K_1:
                        playTrumpet(1)



        clock.tick(fps)


        pygame.display.update()
