import math
import pyautogui

""" Particles """
NBR_TRIANGLE_IN_CIRCLE = 5
CIRCLE_RADIUS = 10/2560 * pyautogui.size()[0]
SUN_PARTICLE_RADIUS = 5
PARTICLE_COLOR = (173, 216, 230)
SUN_PARTICLE_COLOR = (255, 255, 0)
SUN_PARTICLE_COLOR_DELTA = 150
MIN_PARTICLES = 100
MAX_PARTICLES = 100
MIN_SUN_PARTICLES = 300
MAX_SUN_PARTICLES = 300
GRAVITY_MAGNITUDE = 9.81
GRAVITY_DIRECTION = math.pi / 2
SUN_GRAVITY_MAGNITUDE = 1
MARGIN_SUN_PARTICLES = 100

""" Music process """
midi_file = "SSB.mid"
mp3_file = "SSB.mp3"
#midi_file = "Ecossaise_Beethoven.midi"
#mp3_file = "Ecossaise_Both.mp3"

""" Generation """
min_depth = int(600/2560 * pyautogui.size()[0])
max_depth = int(1100/2560 * pyautogui.size()[0])

""" Palm """
NB_PALM = 20