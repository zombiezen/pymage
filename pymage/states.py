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

from __future__ import division

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
__docformat__ = 'reStructuredText'
__all__ = ['State',
           'GLState',
           'Paused',
           'Menu',
           'Game',
           'FakeClock',
           'TwistedGame',]

class State(object):
    """
    Game state that handles events and displays on a surface.
    
    :CVariables:
        bgColor : tuple
            The state's clear color as an RGB 0-255 tuple
        quitOnEscape : bool
            Whether pressing escape quits the game
    """
    bgColor = (0, 0, 0)
    quitOnEscape = False
    
    def __init__(self, bgColor=None):
        if bgColor is not None:
            self.bgColor = bgColor
    
    def handle(self, event):
        """
        Hook method for handling events.
        
        .. Note:: This implementation *should* always be called.
        
        :Parameters:
            event : ``pygame.event.Event``
                Event to handle
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
        
        :Parameters:
            game : `Game`
                Current game
        """
        pass
    
    def firstDisplay(self, screen):
        """
        Hook method for displaying the `State` for the first time.
        
        By default, this merely fills the screen with the background color.
        
        :Parameters:
            screen : ``pygame.Surface``
                Surface to draw to
        """
        screen.fill(self.bgColor)
        pygame.display.flip()       # Swap buffers
    
    def display(self, screen):
        """
        Hook method for drawing the state.
        
        :Parameters:
            screen : ``pygame.Surface``
                Surface to draw to
        """
        pass

class GLState(State):
    """
    Game state with OpenGL-specific drawing.
    
    :CVariables:
        fovy : float
            Horizontal visible field-of-view angle
        clipNear : float
            Near clipping distance
        clipFar : float
            Far clipping distance
        bgColor : tuple
            Clear color as RGBA 0.0-1.0 tuple
    :IVariables:
        camPos : tuple
            Camera position as a (x, y, z) tuple
        camAim : tuple
            Camera aim as a (x, y, z) tuple
        camUpv : tuple
            Camera up vector as a (x, y, z) tuple
    """
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
        """Sets the OpenGL clear color from the `bgColor` attribute."""
        r, g, b = self.bgColor[:3]
        if len(self.bgColor) >= 4:
            a = self.bgColor[4]
        else:
            a = 1.0
        glClearColor(r, g, b, a)
    
    def setupCamera(self, width, height):
        """
        Sets up the OpenGL camera.
        
        This includes setting up the viewport, perspective, and camera position.
        
        :Parameters:
            width : int
                Width of viewport
            height : int
                Height of viewport
        """
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fovy,
                       width / height,
                       self.clipNear,
                       self.clipFar)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.camPos[0], self.camPos[1], self.camPos[2],
                  self.camAim[0], self.camAim[1], self.camAim[2],
                  self.camUpv[0], self.camUpv[1], self.camUpv[2])
    
    def firstDisplay(self, screen):
        """
        Called on first display.
        
        Calls `initGL`, does a ``glClear``, and flips the buffer.
        
        :Parameters:
            screen : ``pygame.Surface``
                Surface to draw to
        """
        self.initGL()
        glClear(GL_COLOR_BUFFER_BIT)
        pygame.display.flip()
    
    def display(self, screen):
        """
        Called on displaying.
        
        Calls `setupGL`, does a ``glClear``, and flips the buffer.
        
        :Parameters:
            screen : ``pygame.Surface``
                Surface to draw to
        """
        self.setupGL()
        glClear(GL_COLOR_BUFFER_BIT)
        pygame.display.flip()

class Paused(State):
    """
    Abstract superclass for simple pause screens that can show text and/or an
    image.
    
    :CVariables:
        image : ``pygame.Surface``
            Image to display in background
        useIM : bool
            Whether to use the image manager to get the image
        text : string
            String to display
        fontSize : int
            Size of the text font
        textColor : tuple
            Text color as an RGBA 0-255 tuple.
        excludedKeys : list
            Keys to ignore
    :IVariables:
        finished : bool
            Whether the state is finished
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
                 bg_color=None,
                 text=None,
                 image=None,
                 fontSize=None,
                 useIM=None):
        super(Paused, self).__init__(bg_color)
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
        """Changes to the next state, if we're done."""
        if self.finished:
            pygame.mouse.set_visible(False)
            game.changeToState(self.nextState())
    
    def firstDisplay(self, screen):
        """Do actual display."""
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
        
        :Raises NotImplementedError: if not overridden
        :ReturnType: `State`
        """
        raise NotImplementedError("Override nextState")

class Menu(State):
    """
    Abstract superclass for menu screens.
    
    :IVariables:
        newState : `State`
            The next state to advance to
        container : `ui.Container`
            The root widget
        cursor : `ui.CursorWidget`
            Visible cursor
    """
    def __init__(self, *args, **kw):
        super(Menu, self).__init__(*args, **kw)
        initRect = pygame.display.get_surface().get_rect()
        self.newState = None
        self.container = ui.Container(bgColor=self.bgColor,
                                      rect=initRect)
        self.cursor = None
        self.body()
    
    def body(self):
        """Adds the menu's contents."""
        pass
    
    def handle(self, event):
        """Dispatches a UI event."""
        super(Menu, self).handle(event)
        self.container.processEvent(event)
        if self.cursor is not None:
            self.cursor.handle(event)
    
    def update(self, game):
        """
        Updates the UI widgets.
        
        If you change the `newState` attribute to a non-``None`` value, it will
        become the new state.
        """
        self.container.update()
        if self.cursor is not None:
            self.cursor.update()
        if self.newState is not None:
            game.changeToState(self.newState)
            self.newState = None
    
    def firstDisplay(self, screen):
        """Sets up the container."""
        self.container.refresh()
        self.container.rect.size = screen.get_size()
        super(Menu, self).firstDisplay(screen)
    
    def display(self, screen):
        """Redisplays any of the widgets that need it."""
        super(Menu, self).display(screen)
        updates = self.container.display(screen)
        if self.cursor is not None:
            updates += self.cursor.display(screen)
        pygame.display.update(updates)

class Game(object):
    """
    Game object that manages the state machine.
    
    :CVariables:
        screenSize : tuple
            Screen size (in pixels) as a (width, height) tuple
        ticks : int
            Capped number of frames per second
        flags : int
            Flags to pass to the display, as described in
            ``pygame.display.set_mode``.
    :IVariables:
        state : `State`
            Current state
        nextState : `State`
            State to advance to
        running : bool
            Whether the game is running
        clock : ``pygame.time.Clock``
            FPS timer
    """
    screenSize = (800, 600)
    ticks = 60
    flags = 0
    
    def __init__(self, root_dir, **kw):
        """
        Initialize game.
        
        :Parameters:
            root_dir : string
                Directory to chdir to.  You can even pass sys.argv[0].
        """
        # Change to root directory (for relative paths)
        os.chdir(os.path.abspath(os.path.dirname(root_dir)))
        # Start with no state
        self.state = self.nextState = None
        self.running = False
        self.screen = None
        self.clock = None
        # Set up instance variables
        self.__dict__.update(kw)
    
    def changeToState(self, state):
        """
        Changes to a state on the next event loop iteration.
        
        :Parameters:
            state : `State`
                State to change to
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
            if event.type == sound.music.endEvent:
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

class FakeClock(object):
    """
    Imitator of ``pygame.time.Clock`` that doesn't delay.
    
    Used for `TwistedGame`.
    """
    def __init__(self):
        self.time = pygame.time.get_ticks()
        self.delta = 0
        self.delay = 0
    
    def get_fps(self):
        """
        Returns the current rate of frames per second.
        
        :ReturnType: float
        """
        return 1 / self.get_time()
    
    def get_rawtime(self):
        """
        Returns number of nondelayed milliseconds between last two calls to
        `tick`.
        
        :ReturnType: int
        """
        return self.delta
    
    def get_delay(self):
        """
        Returns number of delayed milliseconds between last two calls to `tick`.
        
        :ReturnType: int
        """
        return self.delay
    
    def get_time(self):
        """
        Returns number of milliseconds between last two calls to `tick`.
        
        :ReturnType: int
        """
        return self.get_rawtime() + self.get_delay()
    
    def tick(self, ticks=None):
        """
        Keep running at a given framerate.
        
        :Returns: The time since the last call to `tick` in milliseconds.
        :ReturnType: int
        """
        newTime = pygame.time.get_ticks()
        self.delta = newTime - self.time
        self.time = newTime
        if ticks:
            assert ticks > 0
            self.delay = int(max((1 / ticks) * 1000 - self.delta, 0))
        else:
            self.delay = 0
        return self.delta

class TwistedGame(Game):
    """
    Game object that uses a Twisted_ reactor for the main event loop.
    
    .. _Twisted: http://twistedmatrix.com/
    """
    def __init__(self, root_dir, reactor=None, **kw):
        """
        Initialize game object.
        
        :Parameters:
            root_dir : string
                Directory to chdir to.  You can even pass sys.argv[0].
            reactor : Twisted reactor
                Reactor to use for main event loop.  If not specified, then the
                default reactor is used.
        """
        super(TwistedGame, self).__init__(root_dir, **kw)
        if reactor is None:
            from twisted.internet import reactor
        self.reactor = reactor
    
    def run(self):
        """
        Run the game.
        
        This sets up a `FakeClock` object and starts the reactor.
        """
        # Do usual initialization
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize, self.flags)
        self.clock = FakeClock()
        self.preloop()
        self.running = True
        # Iterate will tell the reactor to keep calling it
        self.iterate()
        self.reactor.run()
        # Do post loop
        self.postloop()
    
    def end(self):
        """Stops the game and reactor."""
        super(TwistedGame, self).end()
        self.reactor.stop()
    
    def iterate(self):
        """
        Runs an iteration of the event loop, then tells the reactor to iterate
        again.
        """
        try:
            super(TwistedGame, self).iterate()
            self.reactor.callLater(self.clock.get_delay() / 1000, self.iterate)
        except SystemExit:
            self.end()
