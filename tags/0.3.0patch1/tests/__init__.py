#!/usr/bin/env python
#
#   __init__.py
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

"""Run all tests."""

import unittest

import resmantest
import timertest
import vectortest

__author__ = 'Ross Light'
__date__ = 'July 26, 2006'
__all__ = ['resmantest',
           'timertest',
           'vectortest',
           'test_suite',]

test_suite = unittest.TestSuite([resmantest.test_suite,
                                 timertest.test_suite,
                                 vectortest.test_suite,])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
