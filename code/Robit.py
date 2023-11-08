import pygame
from random import randint
from math import pi
from utils import config

class Robit():
    
    
    def __init__(self, displayWidth=800,displayHeight=480,fps=60,colour=(70, 235, 52),):

        



        self.colour = colour
        self.fps = fps
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight

        self.backgroundColour = (0,0,0)


        self.display = pygame.display.set_mode((displayWidth, displayHeight), pygame.FULLSCREEN)
        pygame.display.set_caption('Robit')
        pygame.mouse.set_visible(False)

        self.fpsClock = pygame.time.Clock()


        # Animations
        self._eyeDim = (150,300)
        self._eyePosL = 100
        self._eyePosR = self.displayWidth - self._eyePosL - self._eyeDim[0]
        self._blinkFramesLeft = 0
        self._smiling = False
        self._winking = False
        self._displayScreen = 'face'
        self.blinkAmbient = True
        self._lastBlink = 0
        self._nextRandomBlink = 300

        #Menu
        




        self._padding = 20
        self._menuLineWidth = 2
        self.settingsImg = self.colorize(pygame.image.load('imgs/settings.png'), self.colour)

        self.settingsImg = pygame.transform.scale(self.settingsImg, (50,50))




    def colorize(self, image, newColor):

            image = image.copy()

            # zero out RGB values
            image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
            # add in new RGB values
            image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

            return image


    def changeColour(self, colour):
        '''Use to change the main colour of all aspects of the display'''
        self.colour = colour
        
    def changeBackground(self, background):
        '''Use to change the background colour of the display'''
        self.backgroundColour = background
    

    def blink(self,duration=15, wink=False):
        '''Triggers a simple blink of the eyes. Set wink=True to make the blink a wink instead'''
        if self._blinkFramesLeft == 0 and self._displayScreen == 'face':
            self._blinkFramesLeft = duration
            self._blinkDuration = duration
            if wink:
                self._winking = True
            else:
                self._winking = False

    def toggleSmile(self):
        '''Toggles whether the mouth is visible or not'''
        if self._displayScreen == 'face':
            self._smiling = not self._smiling


    def toggleMenu(self, animationTime=60):
        '''Changes the current screen being shown. Current arguments taken are 'face' '''

        if self._displayScreen == 'face':
            self._displayScreen = 'opening'
            self._menuOpenFramesLeft = animationTime
            self._menuOpenDuration = animationTime
        
        if self._displayScreen == 'menu':
            self._displayScreen = 'closing'
            self._menuCloseFramesLeft = animationTime
            self._menuCloseDuration = animationTime


    def _menuOpenAnimation(self):
        
        partTime = self._menuOpenDuration / 3
        if self._menuOpenFramesLeft > 2 * partTime:
            # Eye Close
            grad = (self._eyeDim[1] - (2*self._menuLineWidth)) / (partTime)

            intercept = (self._menuOpenDuration * grad) - self._eyeDim[1]

        
            eyeHeight = grad * self._menuOpenFramesLeft - intercept
            eyeYOffset = (self.displayHeight-eyeHeight)/2

            pygame.draw.ellipse(self.display, self.colour, [self._eyePosL,eyeYOffset,150,eyeHeight], 200)
            pygame.draw.ellipse(self.display, self.colour, [self._eyePosR,eyeYOffset,150,eyeHeight], 200)


            self._menuOpenFramesLeft -= 1


        elif self._menuOpenFramesLeft > partTime:
            # Line Extend


            Yrect = (self.displayHeight - 2*self._menuLineWidth) / 2


            grad = (self._eyeDim[0] - (self.displayWidth/2)-self._padding) / partTime
            intercept = (self.displayWidth/2)-self._padding - grad * partTime

            length = grad * self._menuOpenFramesLeft + intercept


            posGrad = (self._eyePosL-self._padding)/partTime
            posIntercept = self._padding - posGrad*partTime


            XLOffset = posGrad*self._menuOpenFramesLeft + posIntercept
            XROffset = self.displayWidth - XLOffset - length
      

            pygame.draw.rect(self.display, self.colour, [XLOffset, Yrect, length, 2*self._menuLineWidth], self._menuLineWidth)
            pygame.draw.rect(self.display, self.colour, [XROffset, Yrect, length, 2*self._menuLineWidth], self._menuLineWidth)

            self._menuOpenFramesLeft -= 1
        elif self._menuOpenFramesLeft > 0:
            # Box up
            self._handleMenu()
            
            grad = (2*self._menuLineWidth-(self.displayHeight-2*self._padding))/partTime
            intercept = self.displayHeight-2*self._padding
            
            height = grad * self._menuOpenFramesLeft + intercept
            
            YOffset = (self.displayHeight-height)/2


            pygame.draw.rect(self.display, self.backgroundColour, [0,0, self.displayWidth, YOffset], 0)
            pygame.draw.rect(self.display, self.backgroundColour, [0,(YOffset+height), self.displayWidth, YOffset], 0)


            pygame.draw.rect(self.display, self.colour, [self._padding, YOffset, (self.displayWidth-2*self._padding), height], self._menuLineWidth)

            self._menuOpenFramesLeft -= 1
        else:
            self._displayScreen = 'menu'

    def _menuCloseAnimation(self):
        partTime = self._menuCloseDuration / 3
        if self._menuCloseFramesLeft > 2 * partTime:
            self._handleMenu()
            # Menu close
            grad = ((self.displayHeight-2*self._padding)-2*self._menuLineWidth)/partTime
            intercept = -(grad*self._menuCloseDuration - (self.displayHeight-2*self._padding))
            height = grad * self._menuCloseFramesLeft + intercept

            YOffset = (self.displayHeight-height)/2

            pygame.draw.rect(self.display, self.backgroundColour, [0,0, self.displayWidth, YOffset], 0)
            pygame.draw.rect(self.display, self.backgroundColour, [0,(YOffset+height), self.displayWidth, YOffset], 0)

            pygame.draw.rect(self.display, self.colour, [self._padding, YOffset, (self.displayWidth-2*self._padding), height], self._menuLineWidth)

            self._menuCloseFramesLeft -=1
        
        elif self._menuCloseFramesLeft > partTime:
            fraction = (self._menuCloseFramesLeft - partTime)/ partTime
            print(fraction)

            length = fraction * (self.displayWidth-2*self._padding)
            Xpos = (self.displayWidth - length)/2
            Ypos = (self.displayHeight - self._menuLineWidth*2)/2

            pygame.draw.rect(self.display, self.colour, [Xpos, Ypos, length, 2*self._menuLineWidth], self._menuLineWidth)

            self._menuCloseFramesLeft -=1

        elif self._menuCloseFramesLeft > 0:
            fraction = 1 - (self._menuCloseFramesLeft / partTime)
            height = self._eyeDim[1] * fraction
            YOffset = (self.displayHeight - height) / 2

            pygame.draw.ellipse(self.display, self.colour, [self._eyePosL, YOffset, self._eyeDim[0], height], 0)
            pygame.draw.ellipse(self.display, self.colour, [self._eyePosR, YOffset, self._eyeDim[0], height], 0)

            self._menuCloseFramesLeft -= 1

        else:
            self._displayScreen = 'face'

    def _handleEyes(self):
        if self._blinkFramesLeft > 0:
            blinkFraction = abs((self._blinkFramesLeft-(self._blinkDuration/2))/(self._blinkDuration/2))
            rightEyeHeight = eyeHeight = blinkFraction * self._eyeDim[1]
            rightEyeYOffset = eyeYOffset = (self.displayHeight-eyeHeight)/2
            self._blinkFramesLeft -= 1
        else:
            rightEyeHeight = eyeHeight = self._eyeDim[1]
            rightEyeYOffset = eyeYOffset = (self.displayHeight - self._eyeDim[1]) / 2
            

        if self._winking:
            rightEyeYOffset = (self.displayHeight - self._eyeDim[1]) / 2
            rightEyeHeight = self._eyeDim[1]

        pygame.draw.ellipse(self.display, self.colour, [self._eyePosL, eyeYOffset, self._eyeDim[0], eyeHeight], 0)
        pygame.draw.ellipse(self.display, self.colour, [self._eyePosR, rightEyeYOffset ,self._eyeDim[0], rightEyeHeight], 0)



    def _handleSmile(self):
        if self._smiling:
            pygame.draw.arc(self.display, self.colour, [275,200,250,200], pi, 2*pi, 5)


    def _handleMenu(self):
        if self._menuOpenFramesLeft == 0:
            pad = self._padding
            pygame.draw.rect(self.display, self.colour, [pad, pad, self.displayWidth-(2*pad),self.displayHeight-(2*pad)], self._menuLineWidth)
        
        
        self.display.blit(self.settingsImg, (400,100))
        self.display.blit(self.settingsImg, (400,300))




    def _randomBlink(self):
        if self._blinkFramesLeft == 0:
            self._lastBlink += 1
            if self._lastBlink == self._nextRandomBlink:
                self.blink(wink=(randint(0,19)==1))
                self._nextRandomBlink = randint(200, 2000)
                self._lastBlink = 0



    def update(self):
        '''Updates the display. To be called at the end of every game loop'''


        #Ambience
        if self.blinkAmbient:
            self._randomBlink()



        # Fill Background
        self.display.fill(self.backgroundColour)


        # Handle display
        if self._displayScreen == 'face':
            self._handleEyes()
            self._handleSmile()
        
        elif self._displayScreen == 'menu':
            self._handleMenu()

        elif self._displayScreen == 'opening':
            self._menuOpenAnimation()
        elif self._displayScreen == 'closing':
            self._menuCloseAnimation()


        # After all
        pygame.display.update()
        self.fpsClock.tick(self.fps)
        
        
        
    


    