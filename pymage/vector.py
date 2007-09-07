#!/usr/bin/env python
#
#   vector.py
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
Manipulate mathematical vectors.

:Variables:
    i : `Vector`
        The x unit vector
    j : `Vector`
        The y unit vector
"""

from __future__ import division
import math

# Get Numeric Python, if we have it
numpy = None
for name in ('numpy', 'Numeric'):
    try:
        numpy = __import__(name, globals())
    except ImportError:
        pass
    else:
        break
del name

__author__ = 'Ross Light'
__date__ = 'March 3, 2006'
__all__ = ['Vector', 'i', 'j']
__docformat__ = 'reStructuredText'

scalarTypes = (int, float, long)

def _getComponents(args, kw):
    """Returns (x, y, z) triple for __init__ arguments."""
    specKw = ('x' in kw, 'y' in kw, 'z' in kw)
    x = kw.pop('x', 0.0)
    y = kw.pop('y', 0.0)
    z = kw.pop('z', 0.0)
    if len(kw) > 0:
        raise TypeError("Unrecognized keyword argument: %s" % list(kw)[0])
    if len(args) == 0:
        pass
    elif len(args) == 1:
        try:
            seq = list(args[0])
        except TypeError:
            # 1D vector
            if specKw[0]:
                raise TypeError("Multiple values for x")
            x = args[0]
        else:
            # Sequence unpack
            if True in specKw:
                raise TypeError("Keyword arguments not allowed on sequences")
            if len(seq) == 0:
                x = y = z = 0.0
            elif len(seq) == 1:
                (x,), y, z = seq, 0.0, 0.0
            elif len(seq) == 2:
                (x, y), z = seq, 0.0
            elif len(seq) == 3:
                (x, y, z) = seq
            else:
                raise TypeError("Sequence with more than 3 values")
    elif len(args) == 2:
        if specKw[0]:
            raise TypeError("Multiple values for x")
        if specKw[1]:
            raise TypeError("Multiple values for y")
        x, y = args
    elif len(args) == 3:
        if specKw[0]:
            raise TypeError("Multiple values for x")
        if specKw[1]:
            raise TypeError("Multiple values for y")
        if specKw[2]:
            raise TypeError("Multiple values for z")
        x, y, z = args
    else:
        raise TypeError("Unrecognized vector creation parameters")
    return (float(x), float(y), float(z))

class Vector(object):
    """
    A three-dimensional vector.
    
    :IVariables:
        x : float
            The x value of the vector
        y : float
            The y value of the vector
        z : float
            The z value of the vector
        magnitude : float
            The length of the vector
        angle : float
            The angle (in degrees) of the vector counterclockwise from the
            positive x-axis.
    """
    
    def __new__(cls, *args, **kw):
        """
        ``Vector(x, y, z)`` -> `Vector`
        ``Vector((x, y, z))`` -> `Vector`
        
        You don't have to specify all three coordinates, only those necessary.
        """
        if cls is Vector:
            if numpy is None:
                return PythonVector.__new__(PythonVector, *args, **kw)
            else:
                return NumericVector.__new__(NumericVector, *args, **kw)
        else:
            return super(Vector, cls).__new__(cls, *args, **kw)
    
    @classmethod
    def findVector(cls, angle, magnitude):
        """
        Finds the two-dimensional vector with the given angle and magnitude.
        
        :Parameters:
            angle : float
                Degrees counterclockwise from the positive x-axis.
            magnitude : float
                Length of the vector.
        :ReturnType: `Vector`
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
        return cls(cos * magnitude, sin * magnitude)
    
    @classmethod
    def twoPointVector(cls, point1, point2):
        """
        Finds the vector with the given points.
        
        The points can be one-, two-, or three-dimensional.
        
        :Parameters:
            point1 : tuple
                An (x, y, z) coordinate describing the first point.
            point2 : tuple
                An (x, y, z) coordinate describing the second point.
        :ReturnType: `Vector`
        """
        return cls(point2) - cls(point1)
    
    # String conversion
    
    def __repr__(self):
        cls = type(self)
        name = '%s.%s' % (cls.__module__, cls.__name__)
        if not self:
            return '%s()' % (name)
        elif self.z == 0:
            return '%s(%g, %g)' % (name, self.x, self.y)
        else:
            return '%s(%g, %g, %g)' % (name, self.x, self.y, self.z)
    
    def __str__(self):
        if self.z == 0:
            return '<%g, %g>' % (self.x, self.y)
        else:
            return '<%g, %g, %g>' % (self.x, self.y, self.z)
    
    # Operations
    
    def __neg__(self):
        return type(self)(-self.x, -self.y, -self.z)
    
    def __pos__(self):
        return type(self)(+self.x, +self.y, +self.z)
    
    def __add__(self, other):
        if isinstance(other, Vector):
            return type(self)(self.x + other.x,
                              self.y + other.y,
                              self.z + other.z)
        else:
            return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Vector):
            return type(self)(self.x - other.x,
                              self.y - other.y,
                              self.z - other.z)
        else:
            return NotImplemented
        
    def __mul__(self, other):
        """
        ``v * x <==> v.__mul__(x)``
        
        x can be a scalar (scalar multiplication) or a `Vector` (dot product).
        """
        if isinstance(other, scalarTypes):      # Scalar
            other = float(other)
            return type(self)(self.x * other,
                              self.y * other,
                              self.z * other)
        elif isinstance(other, Vector):         # Dot Product
            return (self.x * other.x +
                    self.y * other.y +
                    self.z * other.z)
        else:
            return NotImplemented
    
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __div__(self, other):
        # Do true division by default, because that's what one would expect,
        # since our instance variables are floats.
        return self.__truediv__(other)
        
    def __truediv__(self, other):
        if isinstance(other, scalarTypes):      # Scalar
            other = float(other)
            return type(self)(self.x / other,
                              self.y / other,
                              self.z / other)
        else:
            return NotImplemented
        
    def __floordiv__(self, other):
        if isinstance(other, scalarTypes):      # Scalar
            return type(self)(self.x // other,
                              self.y // other,
                              self.z // other)
        else:
            return NotImplemented
    
    def proj(self, other):
        """
        Mathematically: projv u for ``v.proj(u)``.
        
        :Parameters:
            other : `Vector`
                The vector to calculate the projection of.
        :ReturnType: `Vector`
        """
        return (other * self / self.magnitude ** 2) * self
    
    def angleBetween(self, other):
        """
        Obtains the angle between the two vectors in degrees.
        
        :Parameters:
            other : `Vector`
                The vector to calculate the angle between.
        :ReturnType: float
        """
        radianAngle = math.acos((self * other) /
                                (self.magnitude * other.magnitude))
        return math.degrees(radianAngle)
    
    def unitVector(self):
        """
        Creates a vector in the same direction, but of magnitude 1.
        
        :ReturnType: `Vector`
        """
        return self / self.magnitude
    
    def _calcMagnitude(self):
        """Calculate magnitude."""
        if numpy is None:
            sqrt = math.sqrt
        else:
            sqrt = numpy.sqrt
        mag = sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        return float(mag)
    
    def _calcAngle(self):
        """Calculate angle in degrees, ignoring z-axis."""
        if numpy is None or not hasattr(numpy, 'angle'):
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
        else:
            deg = math.degrees(numpy.angle(numpy.complex(self.x, self.y)))
        return float(deg)
    
    # List conversion
    
    def __iter__(self):
        """
        ``iter(v) <==> v.__iter__()``
        
        In sequence, this returns the components of the vector, and leaving z
        out if it is 0.  This is usually what you want, but you can force 2D or
        3D by using `iter2D` and `iter3D`, respectively.
        """
        yield self.x
        yield self.y
        if self.z != 0:
            yield self.z
    
    def iter2D(self):
        """
        Returns an iterator that accesses only the x and y components.
        
        :ReturnType: iterator
        """
        yield self.x
        yield self.y
    
    def iter3D(self):
        """
        Returns an iterator that accesses the x, y, and z components.
        
        :ReturnType: iterator
        """
        yield self.x
        yield self.y
        yield self.z
    
    def list2D(self):
        """
        Returns a list that contains only the x and y components.
        
        :ReturnType: list
        """
        return [self.x, self.y]
    
    def list3D(self):
        """
        Returns a list that contains the x, y, and z components.
        
        :ReturnType: list
        """
        return [self.x, self.y, self.z]
    
    # Comparison
    
    def __eq__(self, other):
        if isinstance(other, Vector):
            return (self.x == other.x and
                    self.y == other.y and
                    self.z == other.z)
        else:
            return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, Vector):
            return (self.x != other.x or
                    self.y != other.y or
                    self.z != other.z)
        else:
            return NotImplemented
    
    def __nonzero__(self):
        return bool(self.x or self.y or self.z)
    
    def __hash__(self):
        return int(self.x) ^ int(self.y) ^ int(self.z)
    
    # Component access
    
    def __setattr__(self, attr, value):
        raise AttributeError("Vector is an immutable object")
    
    def __delattr__(self, attr):
        raise AttributeError("Vector is an immutable object")
    
    def _setattr(self, attr, value):
        """
        The real implementation of __setattr__.
        
        But don't tell anyone!  It's a *secret*.
        """
        super(Vector, self).__setattr__(attr, value)
    
    @property
    def x(self):
        raise NotImplementedError()
    
    @property
    def y(self):
        raise NotImplementedError()
    
    @property
    def z(self):
        raise NotImplementedError()
    
    @property
    def magnitude(self):
        """The length of the vector."""
        try:
            return self._magnitude
        except AttributeError:
            mag = self._calcMagnitude()
            self._setattr('_magnitude', mag)
            return mag
    
    @property
    def angle(self):
        """The angle in degrees from the positive x-axis."""
        try:
            return self._angle
        except AttributeError:
            deg = self._calcAngle()
            self._setattr('_angle', deg)
            return deg

class PythonVector(Vector):
    """Vector implemented in pure Python."""
    
    __slots__ = ['x', 'y', 'z', '_magnitude', '_angle']
    
    def __init__(self, *args, **kw):
        x, y, z = _getComponents(args, kw)
        self._setattr('x', x)
        self._setattr('y', y)
        self._setattr('z', z)

class NumericVector(Vector):
    __slots__ = ['_array', '_magnitude', '_angle']
    
    def __init__(self, *args, **kw):
        x, y, z = _getComponents(args, kw)
        self._setattr('_array', numpy.array([x, y, z]))
    
    # Operations
    
    def __add__(self, other):
        if isinstance(other, NumericVector):
            return type(self)(self._array + other._array)
        else:
            return super(NumericVector, self).__add__(other)
    
    def __sub__(self, other):
        if isinstance(other, NumericVector):
            return type(self)(self._array - other._array)
        else:
            return super(NumericVector, self).__sub__(other)
        
    def __mul__(self, other):
        if isinstance(other, scalarTypes):      # Scalar
            return type(self)(self._array * float(other))
        elif isinstance(other, NumericVector):  # Dot Product
            return float(numpy.dot(self._array, other._array))
        else:
            return super(NumericVector, self).__mul__(other)
    
    def __rmul__(self, other):
        if isinstance(other, scalarTypes):
            return self.__mul__(other)
        else:
            return NotImplemented
    
    def __div__(self, other):
        # Do true division by default, because that's what one would expect,
        # since our instance variables are floats.
        return self.__truediv__(other)
        
    def __truediv__(self, other):
        if isinstance(other, scalarTypes):      # Scalar
            return type(self)(self._array / float(other))
        else:
            return super(NumericVector, self).__truediv__(other)
        
    def __floordiv__(self, other):
        if isinstance(other, scalarTypes):      # Scalar
            return type(self)(self._array / float(other))
        else:
            return super(NumericVector, self).__floordiv__(other)
    
    # Component access
    
    @property
    def x(self):
        return float(self._array[0])
    
    @property
    def y(self):
        return float(self._array[1])
    
    @property
    def z(self):
        return float(self._array[2])

# Special vectors
i = Vector(1, 0)
j = Vector(0, 1)
