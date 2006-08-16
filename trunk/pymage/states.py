#!/usr/bin/env python
#
#   states.py
#   pymage
#
#   Copyright (C) 2006 Ross Light
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#   
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#   
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#   USA
#

"""Manages game states (e.g. paused, levels...)"""

import os
import sys

import pygame
from pygame.locals import *

import sprites
import sound

__author__ = 'Ross Light'
__date__ = 'May 22, 2006'
__all__ = ['State', 'Paused', 'Game']

class State(object):
    """Game state that handles events and displays on a surface."""
    bgColor = (0, 0, 0)
    
    def __init__(self, bgColor=None):
        if bgColor is not None:
             self.bgColor = bgColor
    
    def handle(self, event):
        """
        Hook method for handling events.
        This implementation *should* always be called.
        """
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()
    
    def update(self, game):
        """Hook method for updating the state."""
        pass
    
    def firstDisplay(self, screen):
        """
        Hook method for displaying the State for the first time.
        By default, this merely fils the screen with the background color.
        """
        screen.fill(self.bgColor)
        pygame.display.flip()       # Swap buffers
    
    def display(self, screen):
        """Hook method for drawing the state."""
        pass

class Paused(State):
    """
    Abstract superclass for simple pause screens that can show text and/or an
    image.
    """
    finished = False
    image = None
    useIM = True
    text = ""
    fontSize = 48
    textColor = (0, 0, 0)
    showCursor = False
    
    def __init__(self,
                 bgColor=None,
                 text=None,
                 image=None,
                 fontSize=None,
                 useIM=None):
        super(Paused, self).__init__(bgColor)
        # Set up text
        if text is not None:
            self.text = text
        if fontSize is not None:
            self.fontSize = fontSize
        # Set up image
        if image is not None:
            self.image = image
        if useIM is not None:
            self.useIM = useIM
        if self.useIM and self.image is not None:
            self.image = sprites.ImageManager.loadImage(self.image)
    
    def handle(self, event):
        """Stops the pause screen after a click or key press."""
        State.handle(self, event)
        if event.type in (MOUSEBUTTONDOWN, KEYDOWN, JOYBUTTONDOWN):
            self.finished = True
    
    def update(self, game):
        if self.finished:
            pygame.mouse.set_visible(False)
            game.changeToState(self.nextState())
    
    def firstDisplay(self, screen):
        screen.fill(self.bgColor)   # Clear screen
        font = pygame.font.Font(None, self.fontSize)
        lines = self.text.strip().splitlines()
        # Calculate positioning
        height = len(lines) * font.get_linesize()
        center, top = screen.get_rect().center
        top -= height // 2
        
        # Show image
        if self.image:
            if isinstance(self.image, basestring):
                image = pygame.image.load(self.image).convert_alpha()
            else:
                image = self.image
            imageRect = image.get_rect()
            top += imageRect.height // 2
            imageRect.midbottom = center, top - 20
            screen.blit(image, imageRect)   # show the image
        
        # Render lines
        antialias = True
        for line in lines:
            text = font.render(line.strip(), antialias, self.textColor)
            textRect = text.get_rect()
            textRect.midtop = center, top
            screen.blit(text, textRect)
            top += font.get_linesize()
        
        # Show cursor (if necessary)
        pygame.mouse.set_visible(self.showCursor)
        
        pygame.display.flip()   # swap buffers
    
    def nextState(self):
        """
        Hook method for reaching the next state.  Raises a NotImplementedError
        if not overridden.
        """
        raise NotImplementedError, "Override nextState"

class Game(object):
    """Game object that manages the state machine."""
    screenSize = (800, 600)
    ticks = 60
    flags = 0
    
    def __init__(self, rootDir, **kw):
        # Change to root directory (for relative paths)
        path = os.path.abspath(rootDir)
        dir = os.path.split(path)[0]
        os.chdir(dir)
        # Start with no state
        self.state = self.nextState = None
        # Set up instance variables
        self.__dict__.update(kw)
    
    def changeToState(self, state):
        """Changes to the given state on the next event loop iteration."""
        self.nextState = state
    
    def run(self):
        """
        Run main event loop.
        You shouldn't have to override this...
        """
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize, self.flags)
        self.clock = pygame.time.Clock()
        self.preloop()
        while True:
            self.iterate()
        self.postloop()
    
    def preloop(self):
        """Override this to do something before the event loop starts."""
        pass
    
    def iterate(self):
        """
        Called to perform the event loop.
        You shouldn't have to override the core functionality, but you may wish
        to override this method to do something before or after.
        """
        # Constant FPS, Potter!
        self.clock.tick(self.ticks)
        # Change to the new state (if there is one)
        if self.state != self.nextState:
            self.state = self.nextState
            self.state.firstDisplay(self.screen)
        # Send events to the state
        for event in pygame.event.get():
            if event.type == sound.MusicManager.endEvent:
                sound.MusicManager.nextSong()
            else:
                self.state.handle(event)
        # Update state
        self.state.update(self)
        # Display state
        self.state.display(self.screen)
    
    def postloop(self):
        """Override this to do something after the event loop exits."""
        pass
