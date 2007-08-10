#!/usr/bin/env pythonw
#
#   sound.py
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
pymage sound subsystem

:Variables:
    music : `MusicManager`
        The global music manager
    sound : `SoundManager`
        The global sound manager
"""

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
    
    :CVariables:
        endEvent : int
            The event indicating the end of a song
    :IVariables:
        savedPlaylists : dict of lists
            Saved playlists
        playlist : list
            Current play order
        index : int
            Index of the current song in the current playlist
        loop : bool
            Whether the music should loop
        shouldPlay : bool
            Whether music should be loaded
        playing : bool
            Whether music is playing
        volume : float
            Volume of music (from 0.0 to 1.0)
    """
    endEvent = 25
    
    def __init__(self,
                 should_play=True,
                 loop=True,
                 *args, **kw):
        """
        Initializes the music manager.
        
        :Parameters:
            should_play : bool
                Whether music should be loaded
            loop : bool
                Whether to loop music
            manager : `ResourceManager`
                The resource manager to use.  Default is `pymage.resman.resman`.
        """
        super(MusicManager, self).__init__(*args, **kw)
        self.savedPlaylists = {}
        self.playlist = []
        self.loop = loop
        self.shouldPlay = should_play
        self.index = 0
        self.playing = False
        pygame.mixer.music.set_endevent(self.endEvent)
    
    # Playlist management
    
    def prepare(self, tag, playlist):
        """
        Prepares a playlist for playback later.
        
        .. Warning::
           `prepare` is retained for compatibility reasons.  You should be using
           `addPlaylist` to add new playlists.
        
        :Parameters:
            tag : string
                Name of new playlist
            playlist : list of strings
                Songs in playlist
        """
        warnings.warn("prepare is deprecated; use addPlaylist.",
                      DeprecationWarning,
                      stacklevel=2)
        self.addPlaylist(tag, playlist)
    
    def addPlaylist(self, key, songs):
        """
        Adds a new playlist.
        
        :Parameters:
            key : string
                Name of new playlist
            songs : list of strings
                Songs in new playlist
        """
        self.savedPlaylists[key] = list(songs)
    
    def getPlaylist(self, key):
        """
        Accesses the playlist.
        
        :Parameters:
            key : string
                Name of playlist
        :Returns: List of songs in playlist
        :ReturnType: list
        :Raises KeyError: If playlist does not exist
        """
        return self.savedPlaylists[key]
    
    def removePlaylist(self, key):
        """
        Removes a saved playlist.
        
        :Parameters:
            key : string
                Name of playlist
        :Raises KeyError: If playlist does not exist
        """
        del self.savedPlaylists[key]
    
    # Playback control
    
    def startPlaylist(self, key):
        """
        Starts a playlist denoted by ``key``.
        
        After calling `startPlaylist`, the playlist is *cued*.  You then need to
        call `play` to start playing music.
        
        :Parameters:
            key : string or iterable
                Playlist to play.  If an iterable is passed, then it will be
                used as a temporary playlist.
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
        
        This method will not load anything unless the manager is configured to
        play.
        
        :Parameters:
            key : string
                Name of song.  If not given, the current song is loaded.
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
        
        You can also use the `volume` property.
        """
        return self.volume
    
    def setVolume(self, volume):
        """
        Changes the current volume.
        
        You can also use the `volume` property.
        """
        self.volume = volume
    
    def _getVolume(self):
        """Retrieves the mixer's current volume."""
        return pygame.mixer.music.get_volume()
    
    def _setVolume(self, volume):
        """Changes the mixer's current volume."""
        pygame.mixer.music.set_volume(volume)
    
    volume = property(_getVolume, _setVolume, doc="The mixer's volume")

music = MusicManager()

class SoundManager(resman.Submanager):
    """
    Sound effects manager.
    
    For music, use `MusicManager`.
    
    :IVariables:
        shouldPlay : bool
            Whether sound effects should be loaded
        volume : float
            Volume of played sound effects (from 0.0 to 1.0)
    """
    resourceType = resman.SoundResource
    
    def __init__(self, should_play=True, volume=0.5, *args, **kw):
        """
        Initializes the sound manager.
        
        :Parameters:
            should_play : bool
                Whether sound effects should be loaded
            volume : float
                Volume of played sound effects (from 0.0 to 1.0)
            manager : `ResourceManager`
                The resource manager to use.  Default is `pymage.resman.resman`.
        """
        super(SoundManager, self).__init__(*args, **kw)
        self.shouldPlay = should_play
        self.volume = volume
    
    def getSound(self, *args, **kw):
        """
        Retrieves a sound, using a cache if possible.

        .. Warning::
           `getSound` is deprecated, for favor of the Submanager API.  Use
           `load` instead.
        
        :Parameters:
            key : string
                Name of sound
        :Returns: The sound requested
        :ReturnType: ``pymage.mixer.Sound``
        """
        warnings.warn("getSound is deprecated; use load.",
                      DeprecationWarning,
                      stacklevel=2)
        return self.load(*args, **kw)
    
    def play(self, tag, volume=None, cache=True):
        """
        Plays a sound.
        
        :Parameters:
            tag : string
                Name of sound effect
            volume : float
                Volume of the sound effect.  If not specified, `volume`
                attribute is used
            cache : bool
                Whether the sound will be cached
        :Returns: The playing sound
        :ReturnType: ``pymage.mixer.Sound``
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
