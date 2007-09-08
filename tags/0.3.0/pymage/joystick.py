#!/usr/bin/env python
#
#   joystick.py
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

"""Manage joysticks"""

import pygame
from pygame.locals import *

__author__ = 'Ross Light'
__date__ = 'July 20, 2006'
__all__ = ['Axis']
__docformat__ = 'reStructuredText'

class Axis(object):
    """
    Represents a joystick axis.
    
    :CVariables:
        perfectRange : tuple
            The three magic values for calculating perfect mode.
    :IVariables:
        joy : ``pygame.joystick.Joystick``
            Joystick
        num : int
            Axis number
        invert : bool
            Invert axis (always calculated)
        perfect : bool
            Whether perfect mode is active.  When ``True``, a few extra
            calculations are performed to ensure that the axis is always within
            the -1.0 to 1.0 range.
    """
    perfectRange = (-1.0, 0.0, 1.0)
    perfect = False
    
    def __init__(self, joy, num, invert=False, perfect=None):
        """
        Initializes the axis.
        
        :Parameters:
            joy : ``pygame.joystick.Joystick``
                Joystick
            num : int
                Axis number
            invert : bool
                Invert axis
            perfect : bool
                Whether perfect mode is active.
        """
        self.joy, self.num = joy, num
        self.invert = invert
        if perfect is not None:
            self.perfect = perfect
        if self.perfect:
            self.min, self.max = 0.0, 0.0
            self.offset, self.scale = 0.0, 1.0
    
    def addEntry(self, value):
        """
        If the axis is in perfect mode, calibrate the axis from the information
        given.
        
        .. Tip:: You shouldn't need to use this, instead, use `sample`.
        
        :Parameters:
            value : float
                Raw joystick value
        """
        if self.perfect:
            perfectMin, perfectMid, perfectMax = self.perfectRange
            if value > self.max:
                self.max = value
            elif value < self.min:
                self.min = value
            else:
                return
            # Do cached calculations
            mid = (self.max + self.min) / 2
            self.offset = perfectMid - mid
            self.scale = (perfectMax - perfectMin) / (self.max - self.min)
    
    def sample(self):
        """
        Samples calibration information for the axis.
        
        This method only needs to be called in perfect mode.  It is not
        neccessary in normal mode, but shouldn't take a performance hit, so you
        should probably stick it in your code anyway.
        """
        joy = pygame.joystick.Joystick(self.joy)
        self.addEntry(joy.get_axis(self.num))
    
    def convert(self, raw_value):
        """
        Converts a raw value from the joystick.
        
        .. Tip:: You shouldn't need to use this, instead, use `get`.
        
        :Parameters:
            raw_value : float
                Raw joystick value
        :Returns: Converted value
        :ReturnType: float
        """
        if self.perfect:
            value = (raw_value + self.offset) * self.scale
        else:
            value = raw_value
        if self.invert:
            value = -value
        return value
    
    def get(self):
        """
        Retrieves the current value of the axis.
        
        If the axis is in perfect mode, this performs calculations based on
        previous calibration information to ensure it is perfect.  If in normal
        mode, this retreives the raw value (inverted, if necessary).
        
        :Returns: Axis value
        :ReturnType: float
        """
        joy = pygame.joystick.Joystick(self.joy)
        return self.convert(joy.get_axis(self.num))
