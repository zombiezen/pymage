#!/usr/bin/env python
#
#   sprites.py
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

"""Defines game sprites"""

import warnings

import pygame
from pygame.locals import *

from pymage import resman
from pymage.vector import Vector

__author__ = 'Ross Light'
__date__ = 'May 22, 2006'
__all__ = ['getImage',
           'ImageManager',
           'im',
           'Sprite',
           'Animation',]
__docformat__ = 'reStructuredText'

def getImage(image, tryIM=True):
    """
    Retrieves an image.
    
    Provides a standard way to either pass an image or a string to a function.
    """
    if isinstance(image, pygame.Surface):
        return image
    else:
        if tryIM:
            try:
                return im.load(image)
            except ValueError:
                pass
        return pygame.image.load(image)

class ImageManager(resman.Submanager):
    """Game image manager."""
    resourceType = resman.ImageResource

    def loadImage(self, *args, **kw):
        """
        Loads an image from disk, using a cached representation, if possible.
        
        .. Warning::
           `loadImage` method is deprecated, for favor of the new Submanager
           API.  Use `load` instead.
        """
        warnings.warn("loadImage is deprecated; use load.",
                      DeprecationWarning,
                      stacklevel=2)
        return self.load(*args, **kw)

im = ImageManager()

class Sprite(pygame.sprite.Sprite, object):
    """Abstract superclass for sprites."""
    hpadding = vpadding = 0
    angleTolerance = 0.5
    clamp = True
    
    def __init__(self, image=None):
        """
        Initializes a sprite.
        
        If the ``image`` parameter is omitted, the class variable ``image`` will
        be used.  If the parameter it finally receives is a string, it will try
        to load the image from the `ImageManager`.  If it is not in the
        `ImageManager`, it assumes that it is a path or pygame.Surface.
        """
        pygame.sprite.Sprite.__init__(self)
        if image is None:
            image = self.image
        self.setImage(image)
        self.rect = self.image.get_rect()
        self.area = pygame.display.get_surface().get_rect()
        self.angle = 0.0
    
    def setImage(self, image, tryIM=True):
        """Changes the current image and the revert image variables."""
        self.image = self._image = getImage(image, tryIM).convert_alpha()
    
    def collideBox(self):
        """
        Returns the box used for checking with the `touches` method.
        
        By default, this uses the ``hpadding`` and ``vpadding`` to construct an
        inset box.  Override to have a different collide box.
        """
        # Multiply by two to get all-around coverage
        return self.rect.inflate(self.hpadding * -2, self.vpadding * -2)
    
    def touches(self, other):
        """
        Returns whether the other sprite is actually touching the receiver.
        """
        return self.collideBox().colliderect(other.collideBox())
    
    def updateWithVector(self, v, clamp=None):
        """Moves the sprite with the given vector."""
        self.rect.x += v.x
        self.rect.y += v.y
        if clamp is None:
            clamp = self.clamp
        if clamp:
            self.rect = self.rect.clamp(self.area)
    
    def rotateImage(self):
        """Rotates the sprite's image to the proper angle."""
        if abs(self.angle) < self.angleTolerance:
            self.image = self._image
        else:
            self.image = pygame.transform.rotate(self._image, self.angle)
        self.rect.size = self.image.get_size()

class Animation(Sprite):
    """Superclass for ambient animations."""
    loop = False
    
    def __init__(self, frames=None, loop=None):
        """
        Initializes an animation.
        
        - ``frames`` is a list of pygame.Surfaces or strings.  If not specified,
          it uses the ``frames`` class variable.
        - ``loop`` is a flag specifying whether the animation should
          continuously play or whether it should kill itself after one play.  If
          not specified, it uses the ``loop`` class variable.
        """
        if frames is None:
            frames = self.frames
        self.frames = list(frames)
        if loop is not None:
            self.loop = loop
        self.frameNum = 0
        super(Animation, self).__init__(frames[0])
    
    def update(self):
        self.advance()
    
    def advance(self):
        """Advances to the next frame and dies if it reaches the end."""
        self.frameNum += 1
        if self.frameNum >= len(self.frames):
            if self.loop:
                self.frameNum = 0
            else:
                self.kill()
        else:
            self.setImage(self.frames[self.frameNum])
