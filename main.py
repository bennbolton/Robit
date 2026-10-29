import pygame, sys
from pygame.locals import *
from Robit import Robit


pygame.init()


robit = Robit()



if __name__ == '__main__':

    looping = True
    mousedown = False


    while looping:

         # Get inputs --------
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get() :
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == pygame.K_SPACE:
                    robit.ui.blink()
                if event.key == pygame.K_w:
                    robit.ui.blink(wink=True)
                if event.key == pygame.K_s:
                    robit.ui.toggleSmile()
                if event.key == pygame.K_m:
                    robit.ui.toggleMenu()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_UP and robit._batteryPercent + 25 <= 75:
                    robit.ui._batteryPercent += 25
                    robit.ui._internetPercent += 25
                if event.key == pygame.K_DOWN and robit._batteryPercent - 25 >= 0:
                    robit.ui._batteryPercent -= 25
                    robit.ui._internetPercent -= 25
                if event.key == pygame.K_j:
                    robit.listen()




            if event.type == pygame.MOUSEBUTTONDOWN or mousedown == True:
                robit.ui._handleClick(mx, my)
                mousedown = True

            if event.type == pygame.MOUSEBUTTONUP:
                mousedown = False


    
        # Processing --------
      
            
        


        # Render elements of the game
        
        robit.update()
