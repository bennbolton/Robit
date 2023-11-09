import pygame, sys
from pygame.locals import *
from Robit import Robit


pygame.init()


robit = Robit()



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
                if event.key == pygame.K_UP and robit._batteryPercent + 25 <= 75:
                    robit._batteryPercent += 25
                    robit._internetPercent += 25
                if event.key == pygame.K_DOWN and robit._batteryPercent - 25 >= 0:
                    robit._batteryPercent -= 25
                    robit._internetPercent -= 25
                




                if event.key == pygame.MOUSEBUTTONDOWN:
                    robit._handleClick(mx, my)

    
        # Processing --------
      
    
        


        # Render elements of the game
        
        robit.update()
