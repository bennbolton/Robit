import pygame, sys
from pygame.locals import *

pygame.init()

FPS = 60
fpsClock = pygame.time.Clock()
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480

BACKGROUND = (0,0,0)
GREEN = 70, 235, 52
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Robit')





def main():

    looping = True

    animation_time = 15
    frames_left = 0


    while looping:
    
    # Get inputs --------
        for event in pygame.event.get() :
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN and frames_left == 0:
                frames_left = animation_time
    
    
    # Processing --------
    
    
        


    # Render elements of the game
        WINDOW.fill(BACKGROUND)

        if frames_left > 0:
            var = ((frames_left - 30)**2)/30**2
            height = var * 300
            eyeOffset = (WINDOW_HEIGHT-height)/2
            frames_left -= 1
        else:
            height = 300
            eyeOffset = 90

        pygame.draw.ellipse(WINDOW, GREEN, [100,eyeOffset,150,height], 200)
        pygame.draw.ellipse(WINDOW, GREEN, [550,eyeOffset,150,height], 200)
        pygame.display.update()
        fpsClock.tick(FPS)

main()