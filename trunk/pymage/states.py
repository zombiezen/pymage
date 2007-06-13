#!/usr/bin/env python
#
#   states.py
#   pymage
#
#   Copyright (C) 2006-2007 Ross Light
#
#   This file is part of pymage.
#
#   pymage is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#   
#   pymage is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#   
#   You should have received a copy of the GNU Lesser General Public
#   License along with pymage; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#   USA
#

"""Manages game states (e.g. paused, levels...)"""

import os
import sys

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
except ImportError:
    pass
import pygame
from pygame.locals import *

from pymage import sprites
from pymage import sound
from pymage import ui

__author__ = 'Ross Light'
__date__ = 'May 22, 2006'
__all__ = ['State', 'GLState', 'Paused', 'Menu', 'Game']
__docformat__ = 'reStructuredText'

class State(object):
    """Game state that handles events and displays on a surface."""
    bgColor = (0, 0, 0)
    quitOnEscape = False
    
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
        elif self.quitOnEscape and \
             event.type == KEYDOWN and \
             event.key == K_ESCAPE:
            sys.exit()
    
    def update(self, game):
        """
        Hook method for updating the state.
        
        ``game`` is an instance of `Game`.
        """
        pass
    
    def firstDisplay(self, screen):
        """
        Hook method for displaying the `State` for the first time.
        
        By default, this merely fills the screen with the background color.
        """
        screen.fill(self.bgColor)
        pygame.display.flip()       # Swap buffers
    
    def display(self, screen):
        """Hook method for drawing the `State`."""
        pass

class GLState(State):
    """Game state with OpenGL-specific drawing."""
    # Camera
    fovy = 60.0
    clipNear = 0.1
    clipFar = 100.0
    bgColor = (0.0, 0.0, 0.0, 1.0)
    
    def __init__(self, *args, **kw):
        super(GLState, self).__init__(*args, **kw)
        self.camPos = (2.0, 0.0, 0.0)
        self.camAim = (0.0, 0.0, 0.0)
        self.camUpv = (0.0, 5.0, 0.0)
    
    def initGL(self):
        """Called on first display to initialize OpenGL."""
        surf = pygame.display.get_surface()
        self.setupClearColor()
        self.setupCamera(surf.get_width(), surf.get_height())
    
    def setupGL(self):
        """Called on subsequent displays to setup OpenGL."""
        surf = pygame.display.get_surface()
        self.setupClearColor()
        self.setupCamera(surf.get_width(), surf.get_height())
    
    def setupClearColor(self):
        r, g, b = self.bgColor[:3]
        if len(self.bgColor) >= 4:
            a = self.bgColor[4]
        else:
            a = 1.0
        glClearColor(r, g, b, a)
    
    def setupCamera(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fovy,
                       w / h,
                       self.clipNear,
                       self.clipFar)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.camPos[0], self.camPos[1], self.camPos[2],
                  self.camAim[0], self.camAim[1], self.camAim[2],
                  self.camUpv[0], self.camUpv[1], self.camUpv[2])
    
    def firstDisplay(self, screen):
        self.initGL()
        glClear(GL_COLOR_BUFFER_BIT)
        pygame.display.flip()
    
    def display(self, screen):
        self.setupGL()
        glClear(GL_COLOR_BUFFER_BIT)
        pygame.display.flip()

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
    excludedKeys = []
    
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
        super(Paused, self).handle(event)
        if event.type in (MOUSEBUTTONUP, JOYBUTTONUP) or \
           event.type == KEYUP and event.key not in self.excludedKeys:
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
        Hook method for advancing to the next state.
        
        Raises a ``NotImplementedError`` if not overridden.
        """
        raise NotImplementedError("Override nextState")

class Menu(State):
    """Abstract superclass for menu screens."""
    def __init__(self, *args, **kw):
        super(Menu, self).__init__(*args, **kw)
        initRect = pygame.display.get_surface().get_rect()
        self.newState = None
        self.container = ui.Container(bgColor=self.bgColor,
                                      rect=initRect)
        self.cursor = None
        self.body()
    
    def body(self):
        """
        Adds the menu's contents.
        
        Override in subclasses.  The root widget is the ``container`` attribute.
        You may set the ``cursor`` attribute to a `ui.CursorWidget`.
        """
        pass
    
    def handle(self, event):
        super(Menu, self).handle(event)
        self.container.processEvent(event)
        if self.cursor is not None:
            self.cursor.handle(event)
    
    def update(self, game):
        """
        Updates the UI widgets.
        
        If you change the ``newState`` attribute to a non-``None`` value, it
        will become the new state.
        """
        self.container.update()
        if self.cursor is not None:
            self.cursor.update()
        if self.newState is not None:
            game.changeToState(self.newState)
            self.newState = None
    
    def firstDisplay(self, screen):
        self.container.refresh()
        self.container.rect.size = screen.get_size()
        super(Menu, self).firstDisplay(screen)
    
    def display(self, screen):
        super(Menu, self).display(screen)
        updates = self.container.display(screen)
        if self.cursor is not None:
            updates += self.cursor.display(screen)
        pygame.display.update(updates)

class Game(object):
    """Game object that manages the state machine."""
    screenSize = (800, 600)
    ticks = 60
    flags = 0
    
    def __init__(self, rootDir, **kw):
        # Change to root directory (for relative paths)
        os.chdir(os.path.abspath(os.path.dirname(rootDir)))
        # Start with no state
        self.state = self.nextState = None
        self.running = False
        # Set up instance variables
        self.__dict__.update(kw)
    
    def changeToState(self, state):
        """
        Changes to the given `State` instance on the next event loop iteration.
        """
        self.nextState = state
    
    def run(self):
        """
        Run main event loop.
        
        You *shouldn't* have to override this...
        """
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize, self.flags)
        self.clock = pygame.time.Clock()
        self.preloop()
        self.running = True
        while self.running:
            try:
                self.iterate()
            except SystemExit:
                self.end()
        self.postloop()
    
    def end(self):
        """Ends the game."""
        self.running = False
    
    def preloop(self):
        """Hook method to do something before the event loop starts."""
        pass
    
    def iterate(self):
        """
        Called to perform one iteration of the event loop.
        
        You *shouldn't* have to override the core functionality, but you may
        wish to override this method to do something before or after.
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
                sound.music.nextSong()
            else:
                self.state.handle(event)
        # Update state
        self.state.update(self)
        # Display state
        self.state.display(self.screen)
    
    def postloop(self):
        """Hook method to do something after the event loop exits."""
        pass
