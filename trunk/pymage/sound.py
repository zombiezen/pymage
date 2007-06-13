#!/usr/bin/env pythonw
#
#   sound.py
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

"""pymage sound subsystem"""

import warnings

import pygame
from pygame.locals import *

from pymage import resman

__author__ = 'Ross Light'
__date__ = 'July 19, 2006'
__all__ = ['MusicManager',
           'music',
           'SoundManager',
           'sound',]
__docformat__ = 'reStructuredText'

class MusicManager(resman.Submanager):
    """
    Game music manager.
    
    For sound effects, use `SoundManager`.
    """
    endEvent = 25
    
    def __init__(self,
                 shouldPlay=True,
                 loop=True,
                 *args, **kw):
        super(MusicManager, self).__init__(*args, **kw)
        self.savedPlaylists = {}
        self.playlist = []
        self.loop = loop
        self.shouldPlay = shouldPlay
        self.index = 0
        self.playing = False
        pygame.mixer.music.set_endevent(self.endEvent)
    
    # Playlist management
    
    def prepare(self, tag, playlist):
        """
        Prepares a playlist for playback later.
        
        .. Warning::
           `prepare` is retained for compatibility reasons.  You should be using
           `addPlaylist` to add new resources.
        """
        warnings.warn("prepare is deprecated; use addPlaylist.",
                      DeprecationWarning,
                      stacklevel=2)
        self.addPlaylist(tag, playlist)
    
    def addPlaylist(self, key, songs):
        """Adds a new playlist."""
        self.savedPlaylists[key] = list(songs)
    
    def getPlaylist(self, key):
        """Accesses the playlist."""
        return self.savedPlaylists[key]
    
    def removePlaylist(self, key):
        """Removes a saved playlist."""
        del self.savedPlaylists[key]
    
    # Playback control
    
    def startPlaylist(self, key):
        """
        Starts a playlist denoted by ``key``.
        
        You may pass an iterable object to `startPlaylist`, and the object will
        be used as a playlist.
        
        After calling `startPlaylist`, the playlist is *cued*.  You then need to
        call `play` to start playing music.
        """
        try:
            self.playlist = self.getPlaylist(key)
        except KeyError:
            try:
                self.playlist = list(key)
            except TypeError:
                raise TypeError("Playlist must be added or an iterable object")
        if self.playlist:
            self.index = 0
            self.loadSong()
    
    def play(self):
        """Starts the current song."""
        if self.shouldPlay and not self.playing:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play()
            self.playing = True
    
    def pause(self):
        """
        Pauses the current song.
        
        You can resume using `play`.
        """
        pygame.mixer.music.pause()
        self.playing = False
    
    def stop(self):
        """Stops the current song and goes to the beginning."""
        pygame.mixer.music.stop()
        self.playing = False
    
    def load(self, key=None):
        """
        Manually loads a song.
        
        If no argument is given, the current song in the playlist is loaded.
        This method will not load anything unless the manager is configured to
        play.
        """
        if key is None:
            if self.playlist:
                key = self.playlist[self.index]
            else:
                raise ValueError("No song in the playlist")
        if self.shouldPlay:
            super(MusicManager, self).load(key)
    
    loadSong = load
    
    def previousSong(self):
        """Returns to the previous song in the playlist."""
        if self.playlist:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.playlist) - 1
            self.stop()
            self.loadSong()
        
    def nextSong(self):
        """Advances to the next song in the playlist."""
        if self.playlist:
            playNextSong = self.playing
            self.index += 1
            if self.index >= len(self.playlist):
                self.index = 0
                if not self.loop:
                    playNextSong = False
            self.stop()
            self.loadSong()
            if playNextSong:
                self.play()
    
    # Volume control
    
    def getVolume(self):
        """
        Gets the current volume.
        
        You can also use the ``volume`` property.
        """
        return self.volume
    
    def setVolume(self, volume):
        """
        Changes the current volume.
        
        You can also use the ``volume`` property.
        """
        self.volume = volume
    
    def _getVolume(self):
        return pygame.mixer.music.get_volume()
    
    def _setVolume(self, volume):
        pygame.mixer.music.set_volume(volume)
    
    volume = property(_getVolume, _setVolume)

music = MusicManager()

class SoundManager(resman.Submanager):
    """
    Sound effects manager.
    
    For music, use `MusicManager`.
    """
    resourceType = resman.SoundResource
    
    def __init__(self, shouldPlay=True, volume=0.5, *args, **kw):
        super(SoundManager, self).__init__(*args, **kw)
        self.shouldPlay = shouldPlay
        self.volume = volume
    
    def getSound(self, *args, **kw):
        """
        Retrieves a sound, using a cache if possible.

        .. Warning::
           `getSound` is deprecated, for favor of the Submanager API.  Use
           `load` instead.
        """
        warnings.warn("getSound is deprecated; use load.",
                      DeprecationWarning,
                      stacklevel=2)
        return self.load(*args, **kw)
    
    def play(self, tag, volume=None, cache=True):
        """
        Plays a sound and returns the sound object.
        
        This method will use a cached representation if possible.  Also, you can
        specify a non-default volume, if desired.  The cache flag specifies
        whether the sound will be cached, not whether it uses the cache.
        """
        if volume is None:
            volume = self.volume
        if self.shouldPlay:
            if cache:
                self.cache(tag)
            snd = self.load(tag)
            snd.set_volume(volume)
            snd.play()
            return snd
        else:
            return None

sound = SoundManager()
