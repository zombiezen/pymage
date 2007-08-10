#!/usr/bin/env python
#
#   sprites.py
#   pymage
#
#   Copyright (C) 2006-2007 Ross Light
#
#   This file is part of pymage.
#
#   pymage is free software; you can redistribute it and/or modify it under the
#   terms of the GNU Lesser General Public License as published by the Free
#   Software Foundation; either version 3 of the License, or (at your option)
#   any later version.
#   
#   pymage is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
#   more details.
#   
#   You should have received a copy of the GNU Lesser General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Defines game sprites

:Variables:
    im : `ImageManager`
        Global image manager
"""

import warnings

import pygame
from pygame.locals import *

from pymage import resman

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
    
    :Parameters:
        image : string
            Name of the image resource
        tryIM : bool
            Whether to use the image manager.  If ``False`` or the image manager
            cannot find it, the image is assumed to be a path.
    :Returns: The image requested
    :ReturnType: ``pygame.Surface``
    """
    if isinstance(image, pygame.Surface):
        return image
    else:
        if tryIM:
            try:
                return im.load(image)
            except KeyError:
                pass
        return pygame.image.load(image)

class ImageManager(resman.Submanager):
    """Game image manager."""
    resourceType = resman.ImageResource

    def loadImage(self, *args, **kw):
        """
        Loads an image from disk, using a cached representation, if possible.
        
        .. Warning::
           `loadImage` method is deprecated, in favor of the new Submanager
           API.  Use `load` instead.
        
        :Parameters:
            key : string
                Name of the image resource
        :Returns: The image requested
        :ReturnType: ``pygame.Surface``
        """
        warnings.warn("loadImage is deprecated; use load.",
                      DeprecationWarning,
                      stacklevel=2)
        return self.load(*args, **kw)

im = ImageManager()

class Sprite(pygame.sprite.Sprite, object):
    """
    Abstract superclass for sprites.
    
    :CVariables:
        hpadding : int
            The horizontal padding for the collision box.  See `collideBox`.
        vpadding : int
            The vertical padding for the collision box.  See `collideBox`.
        angleTolerance : float
            The angle tolerance for using the initial image
        clamp : bool
            Whether to clamp the sprite to the screen boundaries
    :IVariables:
        image : ``pygame.Surface``
            The sprite's image
        rect : ``pygame.Rect``
            The sprite's position
        angle : float
            The sprite's angle (in counterclockwise degrees)
        area : ``pygame.Rect``
            The clamping area
    """
    hpadding = vpadding = 0
    angleTolerance = 0.5
    clamp = True
    
    def __init__(self, image=None):
        """
        Initializes a sprite.
        
        :Parameters:
            image : string
                The initial image to use
        """
        pygame.sprite.Sprite.__init__(self)
        if image is None:
            image = self.image
        self.setImage(image)
        self.rect = self.image.get_rect()
        self.area = pygame.display.get_surface().get_rect()
        self.angle = 0.0
    
    def setImage(self, image, tryIM=True):
        """
        Changes the current image and the revert image variables.
        
        :Parameters:
            image : string
                The image name
            tryIM : bool
                Whether to use the image manager
        """
        self.image = self._image = getImage(image, tryIM).convert_alpha()
    
    def collideBox(self):
        """
        Returns the box used for checking with the `touches` method.
        
        By default, this uses the `hpadding` and `vpadding` to construct an
        inset box.  Override to have a different collide box.
        
        :Returns: The collision box
        :ReturnType: ``pygame.Rect``
        """
        # Multiply by two to get all-around coverage
        return self.rect.inflate(self.hpadding * -2, self.vpadding * -2)
    
    def touches(self, other):
        """
        Returns whether the other sprite is actually touching the receiver.
        
        :Parameters:
            other : `Sprite`
                The sprite to test collision with
        :ReturnType: bool
        """
        return self.collideBox().colliderect(other.collideBox())
    
    def updateWithVector(self, vector, clamp=None):
        """
        Moves the sprite with the given vector.
        
        :Parameters:
            vector : `pymage.vector.Vector`
                The vector describing where to move
            clamp : bool
                Whether to clamp to `area`.  If not specified, this depends on
                the `clamp` attribute.
        """
        self.rect.x += vector.x
        self.rect.y += vector.y
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
    """
    Superclass for ambient animations.
    
    :IVariables:
        frames : list of ``pygame.Surface``s or strings
            Individual frames of the animation
        loop : bool
            Whether the animation should continuously play or whether it should
            kill itself after one run
    """
    loop = False
    
    def __init__(self, frames=None, loop=None):
        """
        Initializes an animation.
        
        :Parameters:
            frames : list of ``pygame.Surface``s or strings
                The individual frames of the animation.  If not specified, the
                `frames` class variable is used.
            loop : bool
                Whether the animation should continuously play or whether it
                should kill itself after one run.  If not specified, it uses
                the `loop` class variable.
        """
        if frames is None:
            frames = self.frames
        self.frames = list(frames)
        if loop is not None:
            self.loop = loop
        self.frameNum = 0
        super(Animation, self).__init__(frames[0])
    
    def update(self):
        """
        Updates the sprite.
        
        Default implementation advances to the next frame.
        """
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
