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

import unittest

from pymage.timer import *

__author__ = 'Ross Light'
__date__ = 'May 24, 2007'
__all__ = ['TimerTestCase', 'test_suite',]

class TimerTestCase(unittest.TestCase):
    duration = 5.0
    magic1, magic2 = 'xyzzy', 'ROSEbud'
    
    def setUp(self):
        pass
    
    def callback(self, arg1, arg2):
        self.called = True
        self.assert_(arg1 is self.magic1, "Positional argument lost")
        self.assert_(arg2 is self.magic2, "Keyword argument lost")
    
    def testBasicTimer(self):
        """Basic timer test"""
        timer = Timer(self.duration)
        fireCount = timer.update(self.duration / 2)
        self.assertEqual(fireCount, 0, "Timer fired too early!")
        fireCount = timer.update(self.duration / 2)
        self.assertEqual(fireCount, 1, "Timer firing problem")
        fireCount = timer.update(42)
        self.assertEqual(fireCount, 0, "Timer is trigger-happy")
    
    def testCallback(self):
        """Timer callback test"""
        self.called = False
        timer = Timer(self.duration, 0, self.callback,
                      (self.magic1,), {'arg2': self.magic2})
        fireCount = timer.update(self.duration)
        self.assert_(self.called, "Callback was never called!")
        self.assertEqual(fireCount, 1, "Timer firing problem")
    
    def testLoop(self):
        """Timer loop test"""
        timer = Timer(self.duration, 3)
        fireCount = timer.update(self.duration)
        self.assertEqual(fireCount, 1, "Timer didn't fire right first")
        fireCount = timer.update(self.duration)
        self.assertEqual(fireCount, 1, "Timer didn't fire right second")
        fireCount = timer.update(self.duration * 2)
        self.assertEqual(fireCount, 2, "Timer didn't fire twice")
        fireCount = timer.update(self.duration)
        self.assertEqual(fireCount, 0, "Timer is stuck")

test_suite = unittest.makeSuite(TimerTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
