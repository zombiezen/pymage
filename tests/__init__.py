#!/usr/bin/env python
#
#   __init__.py
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

"""Run all tests."""

__author__ = 'Ross Light'
__date__ = 'July 26, 2006'
__all__ = ['allSuites', 'suite']

import unittest

import vectortest

allSuites = (vectortest.suite,)
test_suite = unittest.TestSuite(allSuites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
