import random
import pygame
#from Demos.win32console_demo import window_size
from pygame import gfxdraw
import pyautogui
import math
import numpy as np
import Point2D
import Constants
import Palm_Generation
from sympy.logic.inference import valid
from win32api import GetSystemMetrics
from Particles import Environment, Force, Vector
from src.Constants import NB_PALM

#TODO : PALM TREE, FILL EMPTY ZONE WITH A FLAT SQUARE, SUN SCALING

pygame.init()

normalScreenSize = 2560

windowWidth = pyautogui.size()[0] - 100/normalScreenSize * pyautogui.size()[0]
windowHeight = pyautogui.size()[1] - 100/normalScreenSize * pyautogui.size()[0]
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

cubes = []
palm_left_possible_pos = []
palm_right_possible_pos = []
palms = []
grounds = []
validGround = []

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

def violet_gradient_color(depth, min_depth=int(600/normalScreenSize * pyautogui.size()[0]), max_depth=int(1100/normalScreenSize * pyautogui.size()[0])):
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

        base_y = pyautogui.size()[1]
        dest = [
            (pyautogui.size()[0]/2-(pyautogui.size()[0]*4)-50/normalScreenSize * pyautogui.size()[0], base_y),
            (pyautogui.size()[0]/2+(pyautogui.size()[0]*4)-50/normalScreenSize * pyautogui.size()[0], base_y),
            (pyautogui.size()[0] -50/normalScreenSize * pyautogui.size()[0] -pyautogui.size()[0]/5, (windowHeight) *7/16 ),
            (-50/normalScreenSize * pyautogui.size()[0] +pyautogui.size()[0]/5, (windowHeight) * 7/16)
        ]

        transfo = get_transformation(src, dest)

        nb_cel = 2

        for i in range(self.rows):
            index = 0
            for j in range(self.cols):
                p1 = (j*cell_width, i*cell_height)
                p2 = ((j + 1) * cell_width, i * cell_height)
                p3 = ((j + 1) * cell_width, (i + 1) * cell_height)
                p4 = ((j * cell_width), (i + 1)* cell_height)

                P1 = apply_transformation(p1, transfo)
                P2 = apply_transformation(p2, transfo)
                P3 = apply_transformation(p3, transfo)
                P4 = apply_transformation(p4, transfo)

                if P1[1] > pyautogui.size()[1]/2 + 10/normalScreenSize * pyautogui.size()[0] and P1[0] > 0 and P2[0] < windowWidth:
                    color = (127,0,255)
                    t1 = Triangle(color, (int(P1[0]),int(P1[1])), (int(P2[0]),int(P2[1])), (int(P3[0]),int(P3[1])) )
                    t2 = Triangle(color, (int(P1[0]),int(P1[1])), (int(P3[0]),int(P3[1])), (int(P4[0]),int(P4[1])) )
                    self.triangles.append(t1)
                    self.triangles.append(t2)

                    cube = Cube(t1, t2)
                    cubes.append(cube)

                    if 2 <= i <= 6:
                        if index < nb_cel:
                            palm_right_possible_pos.append(cube)

                        if  index > nb_cel + 11:
                            palm_left_possible_pos.append(cube)
                    index += 1

            if 2 <= i:
                nb_cel += 2


    def draw(self):
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
                #print("p1:", p1, "p2:", p2, "p3:", p3, "p4:", p4)
                pygame.draw.polygon(window, color, [(0, p1[1]), (0, p3[1]),(windowWidth, p4[1])])
                pygame.draw.polygon(window, color, [(0, p1[1]), (windowWidth, p3[1]),(windowWidth, p2[1])])

    def clear(self):
        self.triangles = []


firstLaunch = True
g = Ground()

# Sort by depth and side
def getSortKey(cube):
    depth = cube.get_depth()
    x_mean = cube.get_xmean()
    if x_mean < pyautogui.size()[0] / 2:
        return (depth, x_mean)   # left side : left to right
    else:
        return (depth, -x_mean)  # right side : right to left

def globalGeneration(screen, time, bpm):
    if firstLaunch:
        g.groundGeneration()
        print("nb cube pour palm a droite : " + str(len(palm_right_possible_pos)))
        print("nb cube pour palm a gauche : " + str(len(palm_left_possible_pos)))

        for i in range(NB_PALM):
            left_cube = palm_left_possible_pos[random.randint(0,len(palm_left_possible_pos)-1)]
            right_cube = palm_right_possible_pos[random.randint(0,len(palm_right_possible_pos)-1)]

            l_pos_x = min(left_cube.p1[0],min(left_cube.p2[0],min(left_cube.p3[0],left_cube.p4[0])))
            r_pos_x = min(right_cube.p1[0],min(right_cube.p2[0],min(right_cube.p3[0],right_cube.p4[0])))

            l_pos_y = min(left_cube.p1[1],min(left_cube.p2[1],min(left_cube.p3[1],left_cube.p4[1])))
            r_pos_y = min(right_cube.p1[1],min(right_cube.p2[1],min(right_cube.p3[1],right_cube.p4[1])))

            print(l_pos_x)
            print(l_pos_y)

            print(r_pos_x)
            print(r_pos_y)

            palm = Palm_Generation.PalmV2(Point2D.Point2D(l_pos_x, l_pos_y))
            palm.generate()
            palms.append(palm)

            palm = Palm_Generation.PalmV2(Point2D.Point2D(r_pos_x, r_pos_y))
            palm.generate()
            palms.append(palm)

        generateValidGround()
        assignCubesToColumns()
        printCubesPerColumn()
        grounds.append(g)
    elif not firstLaunch:
        g.draw()
        cubes_sorted = sorted(validGround, key=getSortKey)

        for cube in cubes_sorted:
            cube.update(pygame.time.get_ticks())
            cube.draw()

        pygame.draw.polygon(window, (255, 255, 255),
                            [(0, windowHeight), (0, validGround[0].p1[1]), (windowWidth, validGround[0].p2[1])])
        pygame.draw.polygon(window, (255, 255, 255),
                            [(0, windowHeight), (windowWidth, windowHeight), (windowWidth, validGround[0].p1[1])])

        for palm in palms:
            palm.manage_palm(screen, time)

font = pygame.font.SysFont("Arial", 30)
def fps_counter(win, clk):
    fps = str(int(clk.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    win.blit(fps_t,(0,0))

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

def changeCubeGrowthSpeed(newSpeed, nbr):
    cubes[nbr].growthSpeed = newSpeed

def changeCubeMaxHeight(newHeight, nbr):
    cubes[nbr].maxHeight = newHeight

def changeCubeAnimiationTime(newAnimiationTime, nbr):
    cubes[nbr].animationTime = newAnimiationTime

def changeCubeStartTime(newStartTime, nbr):
    cubes[nbr].startTime = newStartTime

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
