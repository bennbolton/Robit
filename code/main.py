import pygame, sys
from pygame.locals import *
from Robit import Robit


pygame.init()


robit = Robit(displayWidth=3024, displayHeight=1964)


fpsClock = pygame.time.Clock()


if __name__ == '__main__':

    looping = True



    while looping:

         # Get inputs --------
        mx, my = pygame.mouse.get_pos()
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
                if event.key == pygame.K_m:
                    robit.toggleMenu()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


    
        # Processing --------
      
    
        


        # Render elements of the game
        
        robit.update()
