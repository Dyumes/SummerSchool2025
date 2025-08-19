import Generation
import pygame
from win32api import GetSystemMetrics





#App logic
pygame.init()
window = pygame.display.set_mode((GetSystemMetrics(0) - 100, GetSystemMetrics(1) - 100))
height = 0
clock = pygame.time.Clock()


running = True
while running:

    window.fill((0, 0, 0))
    #t1.draw()
    #s1.draw()
    #t1.update()
    #s1.update()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
            quit()

    clock.tick(60)
    pygame.display.update()

