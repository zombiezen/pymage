#!/usr/bin/env python
#
#   test.py
#

"""Run all tests."""

__author__ = 'Ross Light'
__date__ = 'July 26, 2006'
__all__ = ['allSuites', 'suite']

import unittest

import vectortest

allSuites = (vectortest.suite,)
suite = unittest.TestSuite(allSuites)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
