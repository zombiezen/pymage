#!/usr/bin/env python
#
#   setup.py
#   pymage
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

"""setuptools script for pymage"""

from setuptools import setup
import sys

__author__ = 'Ross Light'
__date__ = 'August 16, 2006'
__all__ = []

if sys.version < '2.4.0':
    print >> sys.stderr, "PyMage requires Python 2.4"
    sys.exit(1)

setup(name="pymage",
      version='0.1.1',
      description="Pygame helper package",
      author="Ross Light",
      author_email='rlight2@gmail.com',
      keywords="pymage pygame",
      url='http://code.google.com/p/pymage/',
      test_suite='tests',
      packages=['pymage'],)
