#!/usr/bin/env python

import sys

import pygame
from pygame.locals import *
import pymage

class HelloState(pymage.states.State):
    quitOnEscape = True
    
    def __init__(self):
        # Call superclass implementation, using a white background
        super(HelloState, self).__init__((255, 255, 255))
        # Perform initialization here...
    
    def handle(self, event):
        super(HelloState, self).handle(event)
        # Handle event here...
    
    def update(self, game):
        # Update game state here...
        pass
    
    def firstDisplay(self, screen):
        super(HelloState, self).firstDisplay(screen)
        # Draw state for first time here and call pygame.display.flip()
    
    def display(self, screen):
        screen.fill(self.bgColor)
        image = pymage.sprites.im.load('Hello')
        rect = pygame.Rect(0, 0, image.get_width(), image.get_height())
        rect.center = screen.get_rect().center
        screen.blit(image, rect)
        pygame.display.flip()

class BasicGame(pymage.states.Game):
    screenSize = (640, 480)
    # Uncomment to run fullscreen
    #flags = FULLSCREEN
    
    def preloop(self):
        pymage.config.setup()                       # Read gamesite.xml file
        pygame.mouse.set_visible(False)             # Hide cursor
        pygame.display.set_caption("Hello World")
        self.changeToState(HelloState())

if __name__ == '__main__':
    BasicGame(sys.argv[0]).run()
