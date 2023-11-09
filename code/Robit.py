import pygame
from random import randint
from math import pi
import os
import speech_recognition as sr

import utils as ut


class Robit():
    
    
    def __init__(self, **kwargs):
        '''Initialise with kwargs to update settings from beginning.
            
            Key words available are: 
            
            displayres ;
            displayfps ;
            fullscreeen ;
            showmouse ;
            accentcolour ;
            backgroundcolour ;
            menupad ;
            menulinethickness ;
            ambientblink'''
        
        ut.updateConfig(**kwargs)

        displayRes = ut.getConfig('displayres')

        self.display = pygame.display.set_mode(displayRes, pygame.FULLSCREEN) if ut.getConfig('fullscreen') else pygame.display.set_mode(displayRes)
        pygame.display.set_caption('Robit')
        pygame.mouse.set_visible(ut.getConfig('showmouse'))

        self.fpsClock = pygame.time.Clock()
        self._totalTicks = 0


        # Animations
        var = 3*displayRes[0]/16
        self._eyeDim = (var, 2*var)
        self._eyePosL = displayRes[0]/8
        self._eyePosR = displayRes[0] - self._eyePosL - self._eyeDim[0]

        self._taskbarIconSize = displayRes[0] / 20
        self._appIconSize = displayRes[0] / 10

        self._blinkFramesLeft = 0
        self._smiling = False
        self._winking = False
        self._displayScreen = 'face'
        self._lastBlink = 0
        self._nextRandomBlink = 300

        self._batteryPercent = 75
        self._internetPercent = 75

        #Menu Icons
        

        self._taskbarIcons = {}
        for image in os.listdir('data/imgs/icons/taskbar'):
            if image[-4:] == '.png':
                path = 'data/imgs/icons/taskbar/' + str(image)
                img = self.colourise(pygame.image.load(path), ut.getConfig('accentcolour'))
                img = pygame.transform.scale(img, (self._taskbarIconSize,self._taskbarIconSize))
                self._taskbarIcons[image[:-4]] = img
            

        self._appIcons = {}
        for image in os.listdir('data/imgs/icons/apps'):
            if image[-4:] == '.png':
                path = 'data/imgs/icons/apps/' + str(image)
                img = self.colourise(pygame.image.load(path), ut.getConfig('accentcolour'))
                img = pygame.transform.scale(img, (self._appIconSize,self._appIconSize))
                self._appIcons[image[:-4]] = img
        #Temp null
        for i in range(7):
            pic = pygame.image.load('data/imgs/icons/apps/settings.png')
            self._appIcons[f'null{i+1}'] = pygame.transform.scale(pic, (self._appIconSize,self._appIconSize))

        self._currentColour = ut.getConfig('accentcolour')

        # Buttons

        padding = ut.getConfig('menupadding')
        lineWidth = ut.getConfig('menulinewidth')
        gapX = ((displayRes[0] - 2*padding-2*lineWidth) - 4 * self._appIconSize) / 5
        initialX = padding + lineWidth + gapX
        gapY = ((displayRes[1] -4*padding -self._taskbarIconSize -4*lineWidth) - 2 * self._appIconSize) / 3
        initialY = 3*padding + 3*lineWidth + self._taskbarIconSize + gapY

        self.appButtons = {}
        for n, app in enumerate(ut.getConfig('homescreen')):
            button = pygame.Rect(initialX + (n%4)*(gapX+self._appIconSize), initialY + (n//4)*(gapY+self._appIconSize), self._appIconSize,self._appIconSize + (self._appIconSize/4))
            self.appButtons[app] = button
        self.appButtons['home'] = pygame.Rect(2*padding+lineWidth,2*padding+lineWidth,self._taskbarIconSize,self._taskbarIconSize)


        #Settings Menu
        self._settingsSlidersPos = [ut.getConfig('accentcolour')[i] for i in range(3)]
        self._settingsSliders = [pygame.Rect(50, 175 + col*50, 255,10) for col in range(3)]
        self._settingsButtons = [pygame.Rect(400,175,50,50)]


        # Text

        titleFont = pygame.font.Font('data/pixel.otf', 40)

        menuTitles = ['Robit Home', 'Settings']
        menuTexts = []
        for title in menuTitles:
            menuTexts.append(titleFont.render(title, True, ut.getConfig('accentcolour')))
        self._menuTitles = dict(zip(menuTitles, menuTexts))


        appFont = pygame.font.Font('data/pixel.otf', 30)
        appTitles = ut.getConfig('homescreen')
        appTexts = []
        for app in self.appButtons:
            appTexts.append(appFont.render(app, True, ut.getConfig('accentcolour')))
        self._appTitles = dict(zip(appTitles,appTexts))

        

    def colourise(self, image, newColor):

            image = image.copy()

            # zero out RGB values
            image.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
            # add in new RGB values
            image.fill(newColor[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

            return image

    def listen(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('Listening....')
            r.pause_threshold = 1
            audio = r.listen(source)    
        try:
            print('Recognizing...')
            query = r.recognize_google(audio, language='en-gb')
            print(query)
        except Exception:
            self.say('Sorry, I could not understand. Could you please say that again?')
            query = None
        return query
    

    def changeColour(self, colour: tuple):
        '''Use to change the main colour of all aspects of the display'''
        ut.updateConfig(accentColour=colour)

        
    def changeBackground(self, background):
        '''Use to change the background colour of the display'''
        ut.updateConfig(backgroundColour=background)
    

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
        '''Toggles whether the mouth is visible or not. (Not Currently available)'''
        if self._displayScreen == 'face':
            self._smiling = not self._smiling


    def toggleMenu(self, animationTime=60):
        '''Changes the current screen being shown. Current arguments taken are 'face' '''

        if self._displayScreen == 'face':
            self._displayScreen = 'opening'
            self._menuOpenFramesLeft = animationTime
            self._menuOpenDuration = animationTime
        
        if self._displayScreen == 'home':
            self._displayScreen = 'closing'
            self._menuCloseFramesLeft = animationTime
            self._menuCloseDuration = animationTime


    def _menuOpenAnimation(self):
        
        colour = ut.getConfig('accentcolour')
        padding = ut.getConfig('menupadding')
        lineWidth = ut.getConfig('menulinewidth')
        displayWidth, displayHeight = ut.getConfig('displayres')

        partTime = self._menuOpenDuration / 3
        if self._menuOpenFramesLeft > 2 * partTime:
            # Eye Close
            grad = (self._eyeDim[1] - (2*lineWidth)) / (partTime)

            intercept = (self._menuOpenDuration * grad) - self._eyeDim[1]

        
            eyeHeight = grad * self._menuOpenFramesLeft - intercept
            eyeYOffset = (displayHeight-eyeHeight)/2

            pygame.draw.ellipse(self.display, colour, [self._eyePosL,eyeYOffset,self._eyeDim[0],eyeHeight], 0)
            pygame.draw.ellipse(self.display, colour, [self._eyePosR,eyeYOffset,self._eyeDim[0],eyeHeight], 0)


            self._menuOpenFramesLeft -= 1


        elif self._menuOpenFramesLeft > partTime:
            # Line Extend


            Yrect = (displayHeight - 2*lineWidth) / 2


            grad = (self._eyeDim[0] - (displayWidth/2)-padding) / partTime
            intercept = (displayWidth/2)-padding - grad * partTime

            length = grad * self._menuOpenFramesLeft + intercept


            posGrad = (self._eyePosL-padding)/partTime
            posIntercept = padding - posGrad*partTime


            XLOffset = posGrad*self._menuOpenFramesLeft + posIntercept
            XROffset = displayWidth - XLOffset - length
      

            pygame.draw.rect(self.display, colour, [XLOffset, Yrect, length, 2*lineWidth], lineWidth)
            pygame.draw.rect(self.display, colour, [XROffset, Yrect, length, 2*lineWidth], lineWidth)

            self._menuOpenFramesLeft -= 1
        elif self._menuOpenFramesLeft > 0:
            # Box up
            self._handleMainMenu()
            backgroundColour = ut.getConfig('backgroundcolour')
            
            grad = (2*lineWidth-(displayHeight-2*padding))/partTime
            intercept = displayHeight-2*padding
            
            height = grad * self._menuOpenFramesLeft + intercept
            
            YOffset = (displayHeight-height)/2


            pygame.draw.rect(self.display, backgroundColour, [0,0, displayWidth, YOffset], 0)
            pygame.draw.rect(self.display, backgroundColour, [0,(YOffset+height), displayWidth, YOffset], 0)


            pygame.draw.rect(self.display, colour, [padding, YOffset, (displayWidth-2*padding), height], lineWidth)

            self._menuOpenFramesLeft -= 1
        else:
            self._displayScreen = 'home'

    def _menuCloseAnimation(self):

        colour = ut.getConfig('accentcolour')
        padding = ut.getConfig('menupadding')
        lineWidth = ut.getConfig('menulinewidth')
        displayWidth, displayHeight = ut.getConfig('displayres')

        partTime = self._menuCloseDuration / 3
        if self._menuCloseFramesLeft > 2 * partTime:
            self._handleMainMenu()
            backgroundColour = ut.getConfig('backgroundcolour')
            # Menu close
            grad = ((displayHeight-2*padding)-2*lineWidth)/partTime
            intercept = -(grad*self._menuCloseDuration - (displayHeight-2*padding))
            height = grad * self._menuCloseFramesLeft + intercept

            YOffset = (displayHeight-height)/2

            pygame.draw.rect(self.display, backgroundColour, [0,0, displayWidth, YOffset], 0)
            pygame.draw.rect(self.display, backgroundColour, [0,(YOffset+height), displayWidth, YOffset], 0)

            pygame.draw.rect(self.display, colour, [padding, YOffset, (displayWidth-2*padding), height], lineWidth)

            self._menuCloseFramesLeft -=1
        
        elif self._menuCloseFramesLeft > partTime:
            fraction = (self._menuCloseFramesLeft - partTime)/ partTime

            length = fraction * (displayWidth-2*padding)
            Xpos = (displayWidth - length)/2
            Ypos = (displayHeight - lineWidth*2)/2

            pygame.draw.rect(self.display, colour, [Xpos, Ypos, length, 2*lineWidth], lineWidth)

            self._menuCloseFramesLeft -=1

        elif self._menuCloseFramesLeft > 0:
            fraction = 1 - (self._menuCloseFramesLeft / partTime)
            height = self._eyeDim[1] * fraction
            YOffset = (displayHeight - height) / 2

            pygame.draw.ellipse(self.display, colour, [self._eyePosL, YOffset, self._eyeDim[0], height], 0)
            pygame.draw.ellipse(self.display, colour, [self._eyePosR, YOffset, self._eyeDim[0], height], 0)

            self._menuCloseFramesLeft -= 1

        else:
            self._displayScreen = 'face'

    def _handleEyes(self):
        displayWidth, displayHeight = ut.getConfig('displayres')
        if self._blinkFramesLeft > 0:
            blinkFraction = abs((self._blinkFramesLeft-(self._blinkDuration/2))/(self._blinkDuration/2))
            rightEyeHeight = eyeHeight = blinkFraction * self._eyeDim[1]
            rightEyeYOffset = eyeYOffset = (displayHeight-eyeHeight)/2
            self._blinkFramesLeft -= 1
        else:
            rightEyeHeight = eyeHeight = self._eyeDim[1]
            rightEyeYOffset = eyeYOffset = (displayHeight - self._eyeDim[1]) / 2
            

        if self._winking:
            rightEyeYOffset = (displayHeight - self._eyeDim[1]) / 2
            rightEyeHeight = self._eyeDim[1]



        colour = ut.getConfig('accentColour')



        pygame.draw.ellipse(self.display, colour, [self._eyePosL, eyeYOffset, self._eyeDim[0], eyeHeight], 0)
        pygame.draw.ellipse(self.display, colour, [self._eyePosR, rightEyeYOffset ,self._eyeDim[0], rightEyeHeight], 0)
        #############
        



    def _handleSmile(self):
        colour = ut.getConfig('accentcolour')
        if self._smiling:
            pass #Need to pygame.draw a new smile here
    

    def _handleGeneralMenu(self, title):
        colour = ut.getConfig('accentcolour')
        padding = ut.getConfig('menupadding')
        lineWidth = ut.getConfig('menulinewidth')
        displayWidth, displayHeight = ut.getConfig('displayres')
            
        pygame.draw.rect(self.display, colour, [padding, padding, displayWidth-(2*padding),displayHeight-(2*padding)], lineWidth)

        
        insideLine = 2*padding + lineWidth
        divideLineY = insideLine + self._taskbarIconSize + padding
        divideLineX = insideLine

        pygame.draw.rect(self.display, colour, [divideLineX, divideLineY, displayWidth-2*divideLineX,2*lineWidth],lineWidth)
        
        self.display.blit(self._taskbarIcons['home'], (divideLineX, insideLine))

        self.display.blit(self._taskbarIcons['battery'+str(self._batteryPercent)], (displayWidth-insideLine-self._taskbarIconSize, insideLine))
        if self._totalTicks % 100 < 50 and self._internetPercent == 0:
            self.display.blit(self._taskbarIcons['internet'+str(self._internetPercent)], (displayWidth-insideLine-self._taskbarIconSize*2-padding, insideLine))
        elif self._internetPercent > 0:
            self.display.blit(self._taskbarIcons['internet'+str(self._internetPercent)], (displayWidth-insideLine-self._taskbarIconSize*2-padding, insideLine))

        self.display.blit(self._menuTitles[title], (insideLine+self._taskbarIconSize+padding, insideLine))


    def _handleMainMenu(self):
        self._handleGeneralMenu('Robit Home')
        
        for app in ut.getConfig('homescreen'):
            x = self.appButtons[app].centerx
            y = self.appButtons[app].top
            rect = self._appTitles[app].get_rect()
            rect.centerx = x
            rect.top = y + self._appIconSize
            self.display.blit(self._appTitles[app], rect)

            self.display.blit(self._appIcons[app], self.appButtons[app])

         
        


    def _handleSettings(self):
        self._handleGeneralMenu('Settings')
        self._handleSlider()

        for button in self._settingsButtons:
            pygame.draw.rect(self.display, 'red', button, width=0)



        
    def _handleClick(self, mx, my):
        if self.appButtons['home'].collidepoint(mx,my):
            self._displayScreen = 'home'

        if self._displayScreen == 'home':
            for screen, button in self.appButtons.items():
                if button.collidepoint(mx,my):
                    self._displayScreen = screen
                
        if self._displayScreen == 'settings':
            for i, slider in enumerate(self._settingsSliders):
                if slider.collidepoint(mx,my):
                    self._settingsSlidersPos[i] = mx
                    num = mx - slider.left
                    colourCopy = list(ut.getConfig('accentcolour'))
                    colourCopy[i] = num
                    ut.updateConfig(accentcolour=tuple(colourCopy))
            for button in self._settingsButtons:
                if button.collidepoint(mx, my):
                    ut.updateConfig(accentcolour=ut.getDefaultConfig('accentcolour'))
                    for i,slider in enumerate(self._settingsSliders):
                        self._settingsSlidersPos[i] = ut.getDefaultConfig('accentcolour')[i] + slider.left
                    

        


    def _handleSlider(self):
        if self._displayScreen == 'settings':
            for col in range(3):
                colour = list(ut.getConfig('accentcolour'))
                for i in range(255):
                    colour[col] = i
                    pygame.draw.rect(self.display, tuple(colour), [50+i, 175 + col*50, 1, 10], 0)

                pygame.draw.circle(self.display, ut.getConfig('accentcolour'), (self._settingsSlidersPos[col], 175 + col*50 +5), 12,0)
                pygame.draw.circle(self.display, 'grey', (self._settingsSlidersPos[col], 175 + col*50 +5), 9,0)


    def _randomBlink(self):
        if self._blinkFramesLeft == 0:
            self._lastBlink += 1
            if self._lastBlink == self._nextRandomBlink:
                self.blink(wink=(randint(0,19)==1))
                self._nextRandomBlink = randint(200, 2000)
                self._lastBlink = 0

    def _updateColours(self, accentColour):
        for img in self._appIcons:
            self._appIcons[img] = self.colourise(self._appIcons[img], accentColour)
        for img in self._taskbarIcons:
            self._taskbarIcons[img] = self.colourise(self._taskbarIcons[img], accentColour)
        for text in self._menuTitles:
            self._menuTitles[text] = self.colourise(self._menuTitles[text], accentColour)
        for text in self._appTitles:
            self._appTitles[text] = self.colourise(self._appTitles[text], accentColour)
        self._currentColour = accentColour



    def update(self):
        '''Updates the display. To be called at the end of every game loop'''

        accentColour = ut.getConfig('accentcolour')
        if self._currentColour != accentColour:
            self._updateColours(accentColour)



        #Ambience
        if ut.getConfig('ambientblink'):
            self._randomBlink()



        # Fill Background
        self.display.fill(ut.getConfig('backgroundcolour'))


        # Handle display
        if self._displayScreen == 'face':
            self._handleEyes()
            self._handleSmile()
        
        elif self._displayScreen == 'home':
            self._handleMainMenu()





        elif self._displayScreen == 'opening':
            self._menuOpenAnimation()
        elif self._displayScreen == 'closing':
            self._menuCloseAnimation()
        elif self._displayScreen == 'settings':
            self._handleSettings()


        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(self.display, 'red', (mx,my), 10)


        
        


        # After all
        pygame.display.update()
        self._totalTicks +=1
        self.fpsClock.tick(ut.getConfig('displayfps'))

        
        
        
        
    


    