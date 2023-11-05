import pygame, sys
from pygame.locals import *
from Robit import Robit

pygame.init()


robit = Robit()

fpsClock = pygame.time.Clock()


if __name__ == '__main__':

    looping = True

    while looping:

         # Get inputs --------
        for event in pygame.event.get() :
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    robit.blink()
                if event.key == pygame.K_w:
                    robit.blink(wink=True)
                if event.key == pygame.K_s:
                    robit.toggleSmile()

    
        # Processing --------
    
    
        


        # Render elements of the game
        robit.update()
