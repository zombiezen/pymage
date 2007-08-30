#!/usr/bin/env python
#
#   timer.py
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

"""Timing utilities"""

from __future__ import division

__author__ = 'Ross Light'
__date__ = 'January 5, 2007'
__all__ = ['Timer',
           'TimerGroup',]
__docformat__ = 'reStructuredText'

class Timer(object):
    """
    Timer that calls a callback after a given amout of time.
    
    :IVariables:
        duration : float
            Length of time (in seconds) between timer firings
        loop : int
            The number of times to loop.  If zero (the default), the timer fires
            only once.  If its a positive integer, it fires that many times plus
            one.  Otherwise, the timer fires indefinitely.
        callback : function
            Function to call when timer fires
        callArgs : tuple
            Additional arguments to pass to callback
        callKw : tuple
            Additional keyword arguments to pass to callback
    """
    def __init__(self,
                 duration,
                 loop=0,
                 callback=None,
                 callArgs=None,
                 callKw=None):
        """
        Initializes the timer.
        
        :Parameters:
            duration : float
                Length of time between timer firings
            loop : int
                The number of times to loop
            callback : function
                Function to call when timer fires
            callArgs : tuple
                Additional arguments to pass to callback
            callKw : tuple
                Additional keyword arguments to pass to callback
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
        
        :Parameters:
            duration : float
                The timer's new duration (if given)
        """
        if duration is not None:
            self.duration = float(duration)
        if self.duration < 0:
            raise ValueError("Duration must be greater than 0")
        self.value = self.duration
    
    def update(self, time):
        """
        Updates the timer count.
        
        :Parameters:
            time : float
                The elapsed time.  This can be a number, in which case it is
                assumed to be the elapsed time in seconds; an object with a
                ``get_time`` method (such as a ``pygame.time.Clock``
                instance); or an object with a ``clock`` attribute, which should
                provide a ``get_time`` method.  The ``get_time`` should return
                the elapsed time in milliseconds.
        :Returns: How many times the timer fired
        :ReturnType: int
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
    """
    A group of `Timer` objects that all update with one call.
    
    :IVariables:
        timers : list
            List of timers in group
    """
    def __init__(self, timers=None):
        """
        Initializes the group.
    
        :Parameters:
            timers : list
                List of timers in group
        """
        if timers is None:
            timers = []
        self.timers = list(timers)
    
    def add(self, timer):
        """
        Adds a timer to the group.
    
        :Parameters:
            timer : `Timer`
                Timer to add.
        """
        self.timers.append(timer)
    
    def create(self, *args, **kw):
        """
        Creates a new timer and adds it to the group.
        
        :See: `Timer.__init__`
        """
        self.add(Timer(*args, **kw))
    
    def remove(self, timer):
        """
        Removes a timer from the group.
    
        :Parameters:
            timer : `Timer`
                Timer to remove.
        """
        self.timers.remove(timer)
    
    def update(self, time):
        """
        Updates all of the timers.
    
        :See: `Timer.update`
        """
        for timer in self:
            timer.update(time)
    
    def __len__(self):
        return len(self.timers)
    
    def __iter__(self):
        return iter(self.timers)
