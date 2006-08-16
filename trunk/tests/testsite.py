#!/usr/bin/env python
#
#   testsite.py
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

"""Module to add the parent directory to sys.path."""

__author__ = 'Ross Light'
__date__ = 'July 26, 2006'
__all__ = []

import os
import sys

parentDir = os.path.join(os.path.dirname(__file__), os.path.pardir)
parentDir = os.path.abspath(parentDir)

if (parentDir not in sys.path and os.path.pardir not in sys.path):
    sys.path.append(parentDir)