#!/usr/bin/env python
#
#   vector.py
#   pymage
#
#   Created by Ross Light on 3/3/06.
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

"""Manipulate mathematical vectors."""

from __future__ import division
from decimal import Decimal
import math

__author__ = 'Ross Light'
__date__ = 'March 3, 2006'
__all__ = ['Vector', 'i', 'j']

scalarClasses = (int, float, long, Decimal)

class Vector(object):
    """
    An n-dimensional vector, where n is between 1 and 3.
    However, some methods assume it is two-dimensional (e.g. angleBetween).
    """
    __slots__ = ['x', 'y', 'z', '_magnitude', '_angle']
    
    def __init__(self, x=0, y=0, z=0):
        """
        Vector(x, y, z) -> Vector
        You don't have to specify all three coordinates, only those necessary.
        """
        super(Vector, self).__setattr__('x', float(x))
        super(Vector, self).__setattr__('y', float(y))
        super(Vector, self).__setattr__('z', float(z))
    
    @classmethod
    def findVector(klass, angle, magnitude):
        """
        Finds the 2-D vector with the given angle and magnitude.
        The angle is in degrees counterclockwise from the positive X-axis.
        This may experience round-off error, since non-Decimal math is
        performed.
        """
        # Put angle in range of [0, 360)
        while angle < 0:
            angle += 360
        while angle >= 360:
            angle -= 360
        # Find angle in radians
        radAngle = math.radians(angle)
        # Catch special cases
        if angle == 90 or angle == 270:
            cos = 0
        else:
            cos = math.cos(radAngle)
        if angle == 0 or angle == 180:
            sin = 0
        else:
            sin = math.sin(radAngle)
        # Create vector
        return klass(cos * magnitude, sin * magnitude)
    
    @classmethod
    def twoPointVector(klass, p1, p2):
        """
        Finds the vector with the given points.
        You can pass in 1-D, 2-D, or 3-D points.
        """
        return klass(p2) - klass(p1)
    
    # String conversion
    
    def __repr__(self):
        """repr(v) <==> v.__repr__()"""
        klass = self.__class__
        name = '%s.%s' % (klass.__module__, klass.__name__)
        if not self:
            return '%s()' % (name)
        elif self.z == 0:
            return '%s(%g, %g)' % (name, self.x, self.y)
        else:
            return '%s(%g, %g, %g)' % (name, self.x, self.y, self.z)
    
    def __str__(self):
        """str(v) <==> v.__str__()"""
        if self.z == 0:
            return '<%g, %g>' % (self.x, self.y)
        else:
            return '<%g, %g, %g>' % (self.x, self.y, self.z)
    
    # Operators
    
    @staticmethod
    def _convertScalar(s):
        return float(s)
    
    def __neg__(self):
        """-v <==> v.__neg__()"""
        return self.__class__(-self.x, -self.y, -self.z)
    
    def __pos__(self):
        """+v <==> v.__pos__()"""
        return self.__class__(+self.x, +self.y, +self.z)
    
    def __add__(u, v):
        """u + v <==> u.__add__(v)"""
        if isinstance(v, Vector):
            return u.__class__(u.x + v.x, u.y + v.y, u.z + v.z)
        else:
            return NotImplemented
    
    def __sub__(u, v):
        """u - v <==> u.__sub__(v)"""
        if isinstance(v, Vector):
            return u.__class__(u.x - v.x, u.y - v.y, u.z - v.z)
        else:
            return NotImplemented
        
    def __mul__(v, other):
        """
        v * x <==> v.__mul__(x)
        x can be a scalar (for scalar multiplication) or a vector (for the dot
        product).
        """
        if isinstance(other, scalarClasses):    # Scalar
            s = v._convertScalar(other)
            return v.__class__(v.x * s, v.y * s, v.z * s)
        elif isinstance(other, Vector):         # Dot Product
            u, v = v, other # For algorithm simplicity
            return u.x * v.x + u.y * v.y + u.z * v.z
        else:
            return NotImplemented
    
    def __rmul__(v, other):
        """s * v <==> v.__rmul__(s)"""
        return v.__mul__(other)
    
    def __pow__(v, s):
        """v ** s <==> v.__pow__(s)"""
        if isinstance(s, (int, long)):  # Scalar
            return v.x ** s + v.y ** s + v.z ** s
        else:
            return NotImplemented
    
    def __div__(v, other):
        """
        v / x <==> v.__div__(x)
        x can be a scalar (for scalar division) or a vector (for dot dividend).
        """
        # Do true division by default, because that's what one would expect,
        # since our instance variables are floats.
        return v.__truediv__(other)
        
    def __truediv__(v, other):
        """
        v / x <==> v.__div__(x)
        x can be a scalar (for scalar division) or a vector (for dot dividend).
        """
        if isinstance(other, scalarClasses):    # Scalar
            s = v._convertScalar(other)
            return v.__class__(v.x / s, v.y / s, v.z / s)
        elif isinstance(other, Vector):         # Dot Product
            u, v = v, other # For algorithm simplicity
            return u.x / v.x + u.y / v.y + u.z / v.z
        else:
            return NotImplemented
        
    def __floordiv__(v, other):
        """
        v // x <==> v.__div__(x)
        x can be a scalar (for scalar division) or a vector (for dot dividend).
        """
        if isinstance(other, scalarClasses):    # Scalar
            s = v._convertScalar(other)
            return v.__class__(v.x // s, v.y // s, v.z // s)
        elif isinstance(other, Vector):         # Dot Product
            u, v = v, other # For algorithm simplicity
            return u.x // v.x + u.y // v.y + u.z // v.z
        else:
            return NotImplemented
    
    def proj(v, u):
        """Mathematically: projv u"""
        return (u * v / v.magnitude ** 2) * v
    
    def angleBetween(u, v):
        """Obtains the angle between the two vectors in degrees."""
        return math.degrees(math.acos((u * v) / (u.magnitude * v.magnitude)))
    
    def unitVector(self):
        """Creates a vector in the same direction, but of magnitude 1."""
        return self / self.magnitude
    
    # List conversion
    
    def __iter__(self):
        """
        iter(v) <==> v.__iter__()
        In sequence, this returns the components of the vector, and leaving z
        out if it is 0.  This is usually what you want, but you can force 2D or
        3D by using iter2D and iter3D, respectively.
        """
        yield self.x
        yield self.y
        if self.z != 0:
            yield self.z
    
    def iter2D(self):
        """Returns an iterator that accesses only the x and y components."""
        yield self.x
        yield self.y
    
    def iter3D(self):
        """Returns an iterator that accesses the x, y, and z components."""
        yield self.x
        yield self.y
        yield self.z
    
    # Comparison
    
    def __eq__(u, v):
        """u == v <==> u.__eq__(v)"""
        if isinstance(v, Vector):
            return u.x == v.x and u.y == v.y and u.z == v.z
        else:
            return NotImplemented
    
    def __ne__(u, v):
        """u != v <==> u.__ne__(v)"""
        if isinstance(v, Vector):
            return u.x != v.x or u.y != v.y or u.z != v.z
        else:
            return NotImplemented
    
    def __nonzero__(self):
        """bool(v) <==> v.__nonzero__()"""
        return bool(self.x or self.y or self.z)
    
    def __hash__(self):
        return int(self.x) ^ int(self.y) ^ int(self.z)
    
    # Component access
    
    def __setattr__(self, attr, value):
        """v.attr = value <==> v.__setattr__(attr, value)"""
        raise AttributeError, "Vector is an immutable object"
    
    def __delattr__(self, attr):
        """del v.attr <==> v.__delattr__(attr)"""
        raise AttributeError, "Vector is an immutable object"
    
    def _getMagnitude(self):
        try:
            return self._magnitude
        except AttributeError:
            mag = math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
            super(Vector, self).__setattr__('_magnitude', mag)
            return mag
    
    def _getAngle(self):
        try:
            return self._angle
        except AttributeError:
            # Find angle in degrees, ignore z-axis
            if self.x == 0:
                if self.y > 0:
                    deg = 90.0
                elif self.y < 0:
                    deg = -90.0
                else:
                    deg = 0.0
            else:
                deg = math.degrees(math.atan(self.y / self.x))
                while deg < 0:
                    deg += 360
                while deg > 360:
                    deg -= 360
            super(Vector, self).__setattr__('_angle', deg)
            return deg
    
    magnitude = property(_getMagnitude)
    angle = property(_getAngle)

# Special vectors
i = Vector(1, 0)
j = Vector(0, 1)
