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

"""Distutils script for pymage"""

from distutils.core import setup
import sys

__author__ = 'Ross Light'
__date__ = 'August 16, 2006'
__all__ = []

if sys.version < '2.4.0':
    print >> sys.stderr, "PyMage requires Python 2.4"
    sys.exit(1)

setup(name="PyMage",
      version='0.1.0',
      description="PyGame helper package",
      author="Ross Light",
      author_email='rlight2@gmail.com',
      url='http://code.google.com/p/pymage/',
      packages=['pymage'],)