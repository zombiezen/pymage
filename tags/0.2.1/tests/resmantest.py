#!/usr/bin/env python
#
#   resmantest.py
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

import os
import unittest

import pygame
from pymage.resman import *

__author__ = 'Ross Light'
__date__ = 'February 28, 2007'
__all__ = ['ResourceManagerTestCase', 'test_suite',]

resourceDirectory = os.path.join(os.path.dirname(__file__), 'data')

class ResourceManagerTestCase(unittest.TestCase):
    resources = {'TestImage': ('test_img.png', ImageResource, [False]),
                 'HelloWorld': ('hello.ogg', SoundResource),}
    groupName = 'group'
    
    def setUp(self):
        # Initialize pygame mixer system
        pygame.mixer.init()
        # Create resource manager
        self.resman = ResourceManager()
        # Add resources to manager
        for key, info in self.resources.iteritems():
            name, resType = info[:2]
            if len(info) == 2:
                args, kw = tuple(), dict()
            elif len(info) == 3:
                args, kw = info[2], dict()
            elif len(info) == 4:
                args, kw = info[2:4]
            else:
                raise RuntimeError("Bad resource description: %r" % info)
            resPath = os.path.join(resourceDirectory, name)
            self.resman.addResource(key, resType(resPath, *args, **kw))
        # Add group with all resources
        self.resman.addCacheGroup(self.groupName, self.resources.keys())
    
    def testIndividualCache(self):
        """Individual resource cache/uncache test"""
        for key in self.resources:
            self.resman.cacheResource(key)
            self.assert_(self.resman.getResource(key).cache is not None,
                         "%r did not create cache" % (key,))
            self.resman.uncacheResource(key)
            self.assert_(self.resman.getResource(key).cache is None,
                         "%r did not destroy cache" % (key,))
    
    def testGroupCache(self):
        """Group resource cache/uncache test"""
        self.resman.cacheGroup(self.groupName)
        for key in self.resources:
            self.assert_(self.resman.getResource(key).cache is not None,
                         "%r did not create cache" % (key,))
        self.resman.uncacheGroup(self.groupName)
        for key in self.resources:
            self.assert_(self.resman.getResource(key).cache is None,
                         "%r did not destroy cache" % (key,))
    
    def testResourcePaths(self):
        """Resource path correctness test"""
        for key, info in self.resources.iteritems():
            resourcePath = self.resman.getResource(key).path
            infoPath = os.path.join(resourceDirectory, info[0])
            self.assertEqual(resourcePath, infoPath,
                             "%r path %r does not match %r)" % (key,
                                                                resourcePath,
                                                                infoPath))
    
    def testRemoval(self):
        """Resource removal test"""
        for key in self.resources:
            self.resman.removeResource(key)
            self.assertRaises(KeyError, self.resman.getResource, key)

test_suite = unittest.makeSuite(ResourceManagerTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
