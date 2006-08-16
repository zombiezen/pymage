#!/usr/bin/env python
#
#   setup.py
#   pymage
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
