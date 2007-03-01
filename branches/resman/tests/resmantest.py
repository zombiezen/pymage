#!/usr/bin/env python
#
#   resmantest.py
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
__all__ = ['ResourceManagerTestCase', 'test_suite',]

import os
import unittest

import pygame
from pymage.resman import *

class ResourceManagerTestCase(unittest.TestCase):
    resources = {'TestImage': ('test_img.png', ImageResource, [False]),
                 'HelloWorld': ('hello.ogg', SoundResource),}
    groupName = 'group'
    resourceDirectory = 'data'
    
    def setUp(self):
        # Initialize pygame mixer system
        pygame.mixer.init()
        # Create resource manager
        self.resman = ResourceManager()
        # Get resource directory
        dataPath = os.path.join(os.path.dirname(__file__),
                                self.resourceDirectory)
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
            resPath = os.path.join(dataPath, name)
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

test_suite = unittest.makeSuite(ResourceManagerTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
