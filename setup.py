#!/usr/bin/env python
#
#   setup.py
#   pymage
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

"""setuptools script for pymage"""

# Run bootstrap setuptools installer
from ez_setup import use_setuptools
use_setuptools()

# Import modules
from setuptools import setup
import sys

__author__ = 'Ross Light'
__date__ = 'August 16, 2006'
__all__ = []

# Check for Python 2.4
if sys.version < '2.4.0':
    print >> sys.stderr, "pymage requires Python 2.4"
    sys.exit(1)

# Call setup function
setup(name="pymage",
      version='0.2.0',
      description="Pygame helper package",
      long_description="""\
pymage is a Python package that simplifies many aspects of Pygame programming
(e.g. resource loading).

Its features include:

* File-based configuration
* Auto-configuring joystick support
* Music playlists
* Vectors
* State machine
* High-level timing""",
      license='LGPL',
      author="Ross Light",
      author_email='rlight2@gmail.com',
      keywords="pygame SDL configuration resource",
      url='http://code.google.com/p/pymage/',
      download_url='http://code.google.com/p/pymage/downloads/list',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment',],
      test_suite='tests',
      packages=['pymage'],
      install_requires=['pygame'],
      zip_safe=True,)
