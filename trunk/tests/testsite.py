#!/usr/bin/env python
#
#   testsite.py
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