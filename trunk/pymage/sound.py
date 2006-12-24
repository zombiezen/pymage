#!/usr/bin/env pythonw
#
#   sound.pyw
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

"""pymage sound subsystem"""

import pygame
from pygame.locals import *

__author__ = 'Ross Light'
__date__ = 'July 19, 2006'
__all__ = ['MusicManager',
           'SoundManager',]
__docformat__ = 'reStructuredText'

class MusicManager(object):
    """
    Singleton class to manage the game's music.
    
    For sound effects, use `SoundManager`.
    
    Before you can use this class, you need to call the `setup` method.
    Playlists then need to be prepared with the `prepare` method, and started
    with the `startPlaylist` method.
    
    Typical order of calls:
    
    1. setup
    2. prepare
    3. startPlaylist
    4. play
    """
    endEvent = 25
    
    @classmethod
    def setup(self,
              shouldPlay=True,
              volume=0.5,
              loop=True,):
        self.tagPlaylists = {}
        self.playlist = []
        self.loop = loop
        self.shouldPlay = shouldPlay
        self.setVolume(volume)
        self.index = 0
        self.playing = False
        pygame.mixer.music.set_endevent(self.endEvent)
    
    @classmethod
    def prepare(self, tag, playlist):
        """Prepares a playlist for playback later."""
        self.tagPlaylists[tag] = list(playlist)
    
    @classmethod
    def startPlaylist(self, tag):
        """
        Starts a playlist denoted by ``tag``.
        
        You may pass an iterable object to `startPlaylist`, and the object will
        be used as a playlist.
        """
        try:
            self.playlist = self.tagPlaylists[tag]
        except KeyError:
            try:
                self.playlist = list(tag)
            except TypeError:
                raise TypeError("Tag must be prepared or an iterable object")
        if self.playlist:
            self.index = 0
            self.loadSong()
    
    @classmethod
    def play(self):
        """Starts the current song."""
        if self.shouldPlay and not self.playing:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                pygame.mixer.music.play()
            self.playing = True
    
    @classmethod
    def pause(self):
        """
        Pauses the current song.
        
        You can resume using `play`.
        """
        pygame.mixer.music.pause()
        self.playing = False
    
    @classmethod
    def stop(self):
        """Stops the current song and goes to the beginning."""
        pygame.mixer.music.stop()
        self.playing = False
    
    @classmethod
    def loadSong(self, songFile=None):
        """
        Manually loads a song.
        
        If no argument is given, the current song in the playlist is loaded.
        This method will not load anything unless the manager is configured to
        play.
        """
        if songFile is None:
            if self.playlist:
                songFile = self.playlist[self.index]
            else:
                raise ValueError("No song in the playlist")
        if self.shouldPlay:
            pygame.mixer.music.load(songFile)
    
    @classmethod
    def previousSong(self):
        """Returns to the previous song in the playlist."""
        if self.playlist:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.playlist) - 1
            self.stop()
            self.loadSong()
        
    @classmethod
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
    
    @classmethod
    def getVolume(self):
        """Gets the current volume."""
        return self._volume
    
    @classmethod
    def setVolume(self, volume):
        """Changes the current volume."""
        self._volume = volume
        pygame.mixer.music.set_volume(self._volume)

class SoundManager(object):
    """
    Singleton class to manage sound effects.
    
    For music, use `MusicManager`.
    
    As with `MusicManager`, this is a singleton class, so use the `setup` method
    before using it.
    """    
    @classmethod
    def setup(self,
              shouldPlay=True,
              volume=0.5):
        self.shouldPlay = shouldPlay
        self.volume = volume
        self.soundPaths = {}
        self.soundCache = {}
    
    @classmethod
    def prepare(self, tag, defaultPath=None):
        """
        Declares a tag for later use.
        
        Although you don't have to use `prepare` before loading a sound, it is
        recommended you do so.  `getSound` will become very confused unless the
        tags you are using are the exact path of the sound (which I **really**
        don't recommend).
        """
        if defaultPath is None:
            defaultPath = tag
        self.soundPaths[tag] = defaultPath
    
    @classmethod
    def cache(self, tag):
        """
        Caches the tag and returns the sound.
        
        This will be done automatically by `getSound` if the ``cache`` flag is
        ``True``, but you may not want your users to have to have a delay when
        you use a new resource.
        """
        if tag in self.soundCache:
            sound = self.soundCache[tag]
        else:
            path = self.soundPaths.get(tag, tag)
            sound = pygame.mixer.Sound(path)
            self.soundCache[tag] = sound
        return sound
    
    @classmethod
    def uncache(self, tag):
        """Removes the sound denoted by ``tag`` from the cache."""
        try:
            del self.soundCache[tag]
        except KeyError:
            pass
    
    @classmethod
    def getSound(self, tag, cache=True):
        """
        Retrieves a sound, using a cache if possible.
        
        The ``cache`` flag specifies whether the sound will be cached, not
        whether it uses the cache.
        """
        if tag in self.soundCache:
            return self.soundCache[tag]
        else:
            if cache:
                return self.cache(tag)
            else:
                path = self.soundPaths.get(tag, tag)
                return pygame.mixer.Sound(path)
    
    @classmethod
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
            snd = self.getSound(tag, cache)
            snd.set_volume(volume)
            snd.play()
            return snd
        else:
            return None
