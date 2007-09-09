#!/usr/bin/env python
#
#   __init__.py
#   pymage
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

"""
Various utilities to simplify Pygame_ development.

:Author: Ross Light
:Copyright: Copyright (C) 2006-2007 Ross Light
:Contact: rlight2@gmail.com
:License:
    pymage is free software; you can redistribute it and/or modify it under the
    terms of the `GNU Lesser General Public License`_ as published by the `Free
    Software Foundation`_; either version 3 of the License, or (at your option)
    any later version.
    
    pymage is distributed in the hope that it will be useful, but **WITHOUT ANY
    WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or
    **FITNESS FOR A PARTICULAR PURPOSE**.  See the `GNU Lesser General Public
    License`_ for more details.
    
    You should have received a copy of the `GNU Lesser General Public License`_
    along with this library.  If not, see http://www.gnu.org/licenses/.

.. _Pygame: http://www.pygame.org/
.. _GNU Lesser General Public License: http://www.gnu.org/licenses/lgpl.html
.. _Free Software Foundation: http://fsf.org/
"""

__author__ = 'Ross Light'
__date__ = 'July 20, 2006'
__all__ = ['config',
           'joystick',
           'resman',
           'sound',
           'sprites',
           'states',
           'timer',
           'ui',
           'vector',
           'vfs',]
__docformat__ = 'reStructuredText'
__version__ = '0.3.0patch1'

from pymage import config
from pymage import joystick
from pymage import resman
from pymage import sound
from pymage import sprites
from pymage import states
from pymage import timer
from pymage import ui
from pymage import vector
from pymage import vfs
