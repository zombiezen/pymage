#!/usr/bin/env python
#
#   vectortest.py
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

__author__ = 'Ross Light'
__date__ = 'July 26, 2006'
__all__ = ['VectorTestCase', 'suite']

import unittest

from pymage.vector import *

class VectorTestCase(unittest.TestCase):
    def setUp(self):
        self.v1 = Vector(4.2, 8.7)          # Our test 2D vector
        self.v2 = Vector(1.125, 1.25, 3.14) # Our test 3D vector
    
    def testVectorFind(self):
        ang, mag = 42.7, 5.7
        v = Vector.findVector(ang, mag)
        # Float math is almost always inaccurate.  So let's almost equal our
        # expected result!
        self.assertAlmostEqual(v.angle, ang, msg="Angle is incorrect")
        self.assertAlmostEqual(v.magnitude, mag, msg="Magnitude is incorrect")
    
    def testImmutable(self):
        oldX = self.v1.x
        self.assertRaises(AttributeError,
                          setattr,
                          self.v1,
                          'x',
                          42)
        self.assertEqual(oldX, self.v1.x,
                         "Variable changed")
    
    def testHashable(self):
        d = {self.v1: False,
             Vector(*self.v1): True}
        self.assertEqual(len(d.keys()), 1, "Invalid hashes")
        # This will test whether the other value overwrote the other.  With
        # Python, using the same key twice sets the value to last defined
        # value (which is True, in this case).
        self.assert_(d[self.v1], "Didn't get the proper value")
    
    def testAngle(self):
        self.assertAlmostEqual(Vector.angleBetween(i, j),
                               90,
                               msg="Perpendicular is not 90 degrees")
    
    def testIter(self):
        self.assertEqual(list(self.v1), [self.v1.x, self.v1.y],
                         "2D vector does not give proper iterator")
        self.assertEqual(list(self.v2), [self.v2.x, self.v2.y, self.v2.z],
                         "3D vector does not give proper iterator")
    
    def testTruth(self):
        self.assert_(not bool(Vector()), "Zero vector is True")
        self.assert_(bool(self.v1), "Nonzero vector is False")
    
    def testEquality(self):
        self.assertEqual(self.v1, Vector(*self.v1),
                         "2D vector is not equal to copy")
        self.assertEqual(self.v2, Vector(*self.v2),
                         "3D vector is not equal to copy")
    
    def testInequality(self):
        self.assertNotEqual(self.v1, self.v2,
                            "2D vector is equal to 3D vector")
    
    def testAddSub(self):
        self.assertEqual(self.v1 + self.v2 - self.v2, self.v1,
                         "Adding and subtracting is non-functional")
    
    def testMulDiv(self):
        scalar = 3.14
        self.assertEqual(self.v1 * scalar / scalar, self.v1,
                         "Multiplying and dividing is non-functional")
    
    def testUnitVector(self):
        self.assertAlmostEqual(self.v1.unitVector().magnitude, 1,
                               msg="Unit vectors do not have length of 1")

suite = unittest.makeSuite(VectorTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
