import pygame
from random import randint
from math import pi

class Robit():
    
    
    def __init__(self, displayWidth=800,displayHeight=480,fps=60,colour=(70, 235, 52),):
        self.colour = colour
        self.fps = fps
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight

        self.backgroundColour = (0,0,0)


        self.display = pygame.display.set_mode((displayWidth, displayHeight))
        pygame.display.set_caption('Robit')

        self.fpsClock = pygame.time.Clock()


        # Animations
        self._blinkFramesLeft = 0
        self._smiling = False
        self._winking = False



    def changeColour(self, colour):
        self.colour = colour
        
    def changeBackground(self, background):
        self.backgroundColour = background
    

    def blink(self,duration=15, wink=False): # add wink functionality
        if self._blinkFramesLeft == 0:
            self._blinkFramesLeft = duration
            self._blinkDuration = duration
        if wink:
            self._winking = True
        else:
            self._winking = False

    def toggleSmile(self):
        self._smiling = not self._smiling



    def _handleEyes(self):
        if self._blinkFramesLeft > 0:
            blinkFraction = abs((self._blinkFramesLeft-(self._blinkDuration/2))/(self._blinkDuration/2))
            rightEyeHeight = eyeHeight = blinkFraction * 300 # Make changeable eye dimensions
            rightEyeYOffset = eyeYOffset = (self.displayHeight-eyeHeight)/2
            self._blinkFramesLeft -= 1
        else:
            rightEyeHeight = eyeHeight = 300
            rightEyeYOffset = eyeYOffset = 90

        if self._winking:
            rightEyeYOffset = 90
            rightEyeHeight = 300

        pygame.draw.ellipse(self.display, self.colour, [100,eyeYOffset,150,eyeHeight], 200)
        pygame.draw.ellipse(self.display, self.colour, [550,rightEyeYOffset,150,rightEyeHeight], 200)



    def _handleSmile(self):
        if self._smiling:
            pygame.draw.arc(self.display, self.colour, [275,200,250,200], pi, 2*pi, 5)

    def update(self):
        # Fill Background
        self.display.fill(self.backgroundColour)
        
        # Handle Eyes

        self._handleEyes()

        self._handleSmile()



        # After all
        pygame.display.update()
        self.fpsClock.tick(self.fps)
        
        
        
    


    