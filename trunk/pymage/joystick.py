#!/usr/bin/env python
#
#   joystick.py
#   pymage
#

"""Manage joysticks"""

import pygame
from pygame.locals import *

__author__ = 'Ross Light'
__date__ = 'July 20, 2006'
__all__ = ['Axis']

class Axis(object):
    """
    Represents a joystick axis.
    There is an attribute, perfect, that is defaulted to false.  When true, a
    few extra calculations are performed to ensure that the axis is always
    within the -1.0 to 1.0 range.  Otherwise, the only calculation performed is
    inversion.
    """
    perfMin = -1.0
    perfMid = 0.0
    perfMax = 1.0
    perfect = False
    
    def __init__(self, joy, num, invert=False, perfect=None):
        self.joy, self.num = joy, num
        self.invert = invert
        if perfect is not None:
            self.perfect = perfect
        if self.perfect:
            self.min, self.max = 0.0, 0.0
            self.offset, self.scale = 0.0, 1.0
    
    def addEntry(self, n):
        """
        If the axis is in perfect mode, this calibrates the axis from the
        information given.  You shouldn't need to use this, instead, use sample.
        """
        if self.perfect:
            if n > self.max:
                self.max = n
            elif n < self.min:
                self.min = n
            else:
                return
            # Do cached calculations
            mid = self.min + (self.max - self.min) / 2
            self.offset = self.perfMid - mid
            self.scale = (self.perfMax - self.perfMin) / (self.max - self.min)
    
    def sample(self):
        """
        Samples calibration info for the axis.
        This method only needs to be called in perfect mode.  It is not
        neccessary in normal mode, but shouldn't take a performance hit, so you
        should probably stick it in your code anyway.
        """
        joy = pygame.joystick.Joystick(self.joy)
        self.addEntry(joy.get_axis(self.num))
    
    def convert(self, rawValue):
        """
        Converts a raw value from the joystick.
        You shouldn't need to use this, instead, use get.
        """
        if self.perfect:
            val = (rawValue + self.offset) * self.scale
        else:
            val = rawValue
        
        if self.invert:
            val = -val
        return val
    
    def get(self):
        """
        Retrieves the current value of the axis.
        If the axis is in perfect mode, this performs calculations based on
        previous calibration information to ensure it is perfect.  If in normal
        mode, this retreives the raw value (inverted, if necessary).
        """
        joy = pygame.joystick.Joystick(self.joy)
        return self.convert(joy.get_axis(self.num))