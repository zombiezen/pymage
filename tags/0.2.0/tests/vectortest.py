#!/usr/bin/env python
#
#   vectortest.py
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

import unittest

from pymage.vector import *

__author__ = 'Ross Light'
__date__ = 'July 26, 2006'
__all__ = ['VectorTestCase', 'test_suite',]

class VectorTestCase(unittest.TestCase):
    def setUp(self):
        self.v1 = Vector(4.2, 8.7)          # Our test 2D vector
        self.v2 = Vector(1.125, 1.25, 3.14) # Our test 3D vector
    
    def testVectorCreation(self):
        """Vector creation test"""
        x, y, z = -5.7, 42, 3.14
        vectors = {'a3k0': Vector(x, y, z),
                   'a2k1': Vector(x, y, z=z),
                   'a1k2': Vector(x, y=y, z=z),
                   'a0k3': Vector(x=x, y=y, z=z),
                   'seq': Vector((x, y, z)),
                   'copy': Vector(Vector(x, y, z)),}
        for key, vec in vectors.iteritems():
            self.assertEqual(vec.x, x, msg="%s.x is incorrect" % (key))
            self.assertEqual(vec.y, y, msg="%s.y is incorrect" % (key))
            self.assertEqual(vec.z, z, msg="%s.z is incorrect" % (key))
        self.assertRaises(TypeError, Vector, x, x=x)
        self.assertRaises(TypeError, Vector, (x, y, z), x=x)
    
    def testVectorFind(self):
        """Vector angle/magnitude test"""
        ang, mag = 42.7, 5.7
        v = Vector.findVector(ang, mag)
        # Float math is almost always inaccurate.  So let's almost equal our
        # expected result!
        self.assertAlmostEqual(v.angle, ang, msg="Angle is incorrect")
        self.assertAlmostEqual(v.magnitude, mag, msg="Magnitude is incorrect")
    
    def testImmutable(self):
        """Vector immutability test"""
        oldX = self.v1.x
        self.assertRaises(AttributeError,
                          setattr,
                          self.v1,
                          'x',
                          42)
        self.assertEqual(oldX, self.v1.x,
                         "Variable changed")
    
    def testHashable(self):
        """Vector hash test"""
        d = {self.v1: False,
             Vector(self.v1): True}
        self.assertEqual(len(d.keys()), 1, "Invalid hashes")
        # This will test whether the other value overwrote the other.  With
        # Python, using the same key twice sets the value to last defined
        # value (which is True, in this case).
        self.assert_(d[self.v1], "Didn't get the proper value")
    
    def testAngle(self):
        """Vector angle test"""
        self.assertAlmostEqual(Vector.angleBetween(i, j),
                               90,
                               msg="Perpendicular is not 90 degrees")
    
    def testIter(self):
        """Vector iterator test"""
        self.assertEqual(list(self.v1), [self.v1.x, self.v1.y],
                         "2D vector does not give proper iterator")
        self.assertEqual(list(self.v2), [self.v2.x, self.v2.y, self.v2.z],
                         "3D vector does not give proper iterator")
    
    def testTruth(self):
        """Vector truth value test"""
        self.assert_(not bool(Vector()), "Zero vector is True")
        self.assert_(bool(self.v1), "Nonzero vector is False")
    
    def testEquality(self):
        """Vector equality test"""
        self.assertEqual(self.v1, Vector(self.v1),
                         "2D vector is not equal to copy")
        self.assertEqual(self.v2, Vector(self.v2),
                         "3D vector is not equal to copy")
    
    def testInequality(self):
        """Vector inequality test"""
        self.assertNotEqual(self.v1, self.v2,
                            "2D vector is equal to 3D vector")
    
    def testAddSub(self):
        """Vector addition/subtraction test"""
        self.assertEqual(self.v1 + self.v2 - self.v2, self.v1,
                         "Adding and subtracting is non-functional")
    
    def testMulDiv(self):
        """Vector scalar multiplication/division test"""
        scalar = 3.14
        self.assertEqual(self.v1 * scalar / scalar, self.v1,
                         "Multiplying and dividing is non-functional")
    
    def testUnitVector(self):
        """Unit vector test"""
        self.assertAlmostEqual(self.v1.unitVector().magnitude, 1,
                               msg="Unit vectors do not have length of 1")

test_suite = unittest.makeSuite(VectorTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
