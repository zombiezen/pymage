#!/usr/bin/env python
#
#   timer.py
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

"""Timing utilities"""

from __future__ import division

__author__ = 'Ross Light'
__date__ = 'January 5, 2007'
__all__ = ['Timer',
           'TimerGroup',]
__docformat__ = 'reStructuredText'

class Timer(object):
    """Timer that calls a callback after a given amout of time."""
    def __init__(self,
                 duration,
                 loop=0,
                 callback=None,
                 callArgs=None,
                 callKw=None):
        """
        Initializes the timer.

        ``duration`` is the length of time, in seconds, before the timer fires.

        ``loop`` specifies whether the timer should fire multiple times.  If the
        parameter is 0 (the default), the timer fires only once.  If the
        parameter is a positive integer, it fires that many times plus one.
        Otherwise, the timer fires indefinitely.

        ``callback`` is the function to be called when the timer fires.  It
        usually takes no arguments, but additional ones can be specified using
        ``callArgs`` and ``callKw``.
        """
        self.callback = callback
        if callArgs is None:
            self.callArgs = []
        else:
            self.callArgs = list(callArgs)
        if callKw is None:
            self.callKw = {}
        else:
            self.callKw = dict(callKw)
        self.duration = float(duration)
        self.loop = loop
        self.reset()

    def reset(self, duration=None):
        """
        Resets the timer.

        If ``duration`` is specified, the timer's duration is set to the given
        value.
        """
        if duration is not None:
            self.duration = float(duration)
        if self.duration < 0:
            raise ValueError("Duration must be greater than 0")
        self.value = self.duration

    def update(self, time):
        """
        Updates the timer count.

        Returns how many times the timer fired.

        The value of ``time`` can be a number, in which case it is assumed to be
        the elapsed time in seconds; an object with a ``get_time`` method (such
        as a ``pygame.time.Clock`` instance); or an object with a ``clock``
        attribute, which should provide a ``get_time`` method.  The ``get_time``
        should return the elapsed time in milliseconds.
        """
        # If we're done, do nothing
        if self.loop == 0 and self.value == 0:
            return 0
        # Get the time elapsed
        if hasattr(time, 'get_time'):
            time = time.get_time() / 1000
        elif hasattr(time, 'clock'):
            time = time.clock.get_time() / 1000
        else:
            try:
                time = float(time)
            except TypeError:
                raise TypeError("Unknown type given to Timer.update()")
        # Fire as many times as necessary
        fireCount = 0
        self.value -= time
        while self.value <= 0:
            fireCount += 1
            self.value += self.duration
            if self.callback is not None:
                self.callback(*self.callArgs, **self.callKw)
            if self.loop == 0:
                self.value = 0.0
                break
            elif self.loop > 0:
                self.loop -= 1
        return fireCount

class TimerGroup(object):
    """A group of `Timer` objects that all update with one call."""
    def __init__(self, timers=None):
        if timers is None:
            timers = []
        self.timers = list(timers)
    
    def add(self, timer):
        """Adds a timer to the group."""
        self.timers.append(timer)
    
    def create(self, *args, **kw):
        """
        Creates a new timer and adds it to the group.
        
        The arguments are the same as `Timer.__init__`.
        """
        self.add(Timer(*args, **kw))
    
    def remove(self, timer):
        """Removes a timer from the group."""
        self.timers.remove(timer)
    
    def update(self, time):
        """Updates all of the timers."""
        for timer in self:
            timer.update(time)
    
    def __len__(self):
        return len(self.timers)
    
    def __iter__(self):
        return iter(self.timers)