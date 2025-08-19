import pygame
import math
import array as ar
import pygame_widgets
from fontTools.ttLib.tables.C_P_A_L_ import Color
from pygame_widgets.textbox import TextBox
from matplotlib.widgets import Slider
from win32api import GetSystemMetrics

#Display pygame with a bit smaller resolution than the screen itself

pygame.init()

window = pygame.display.set_mode((GetSystemMetrics(0) - 100, GetSystemMetrics(1) - 100))

clock = pygame.time.Clock()

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


class Mountain:
    def __init__(self, position):
        self.position = position
        self.height = 0
        self.maxReached = False
        self.triangles = []

    def update(self):
        if not self.maxReached:
            self.height += 1
            if self.height >= 200:
                self.height = 200
                self.maxReached = True
        else:
            self.height -= 1
            if self.height <= 0:
                self.height = 0
                self.maxReached = False

    def createMountain(self):
        for t in range(5):
            tri = Triangle((255, 0, 0), (self.position[0], self.position[1]), (150, 300 - self.height), (300, 400))
            self.triangles.append(tri)

    def draw(self):
        pygame.draw.polygon(window, (255, 0, 0), [[self.position[0], self.position[1]], [150 + self.position[0], 300 - self.height], [300, 400]])

        pygame.draw.polygon(window, (0, 255, 0), [[self.position[0], self.position[1]], [75, 400 - self.height], [150 + self.position[0], 300 - self.height]])

mountains = []

def spawnMountain():
    positionX = (GetSystemMetrics(0) - 100) / 18
    positionY = (GetSystemMetrics(1) - 100) / 12

    for m in range(11):
        mountain = Mountain((positionX, positionY))
        mountains.append(mountain)

        positionX += positionX
        positionY += positionY

t1 = Mountain((100, 400))
s1 = Sun((GetSystemMetrics(0) - 100) / 2, (GetSystemMetrics(1) - 100)/1.8, 16, 100)

def globalGeneration():
    t1.draw()
    s1.draw()
    t1.update()
    s1.update()

running = True
while running:

    window.fill((0, 0, 0))

    globalGeneration()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
            quit()

    clock.tick(60)
    pygame.display.update()

