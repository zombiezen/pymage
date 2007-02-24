#!/usr/bin/env python
#
#   resman.py
#   pymage
#
#   Copyright (C) 2007 Ross Light
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

"""Handles all resources"""

import pygame

__author__ = 'Ross Light'
__date__ = 'February 19, 2007'
__all__ = ['ResourceManager',
           'resman',
           'Resource',
           'ImageResource',
           'AudioResource',
           'SoundResource',
           'MusicResource',]
__docformat__ = 'reStructuredText'

class ResourceManager(object):
    """
    Master resource manager.
    
    The resource manager does not directly load resources, but it stores
    resource information for later use.  All of the resources should be added
    to the manager (via `addResource`) when the program starts.  Each resource
    will be assigned a key, which is what is used to access that resource from
    then on.  The resource can then be loaded, cached, and accessed by that key.
    
    One can also create cache groups, sets of resources that can be cached and
    uncached in bulk.  Multiple cache groups can have the same resource in them;
    when no cache groups are caching a given resource, the resource's cache is
    destroyed.
    """
    def __init__(self):
        """
        Initialize the resource manager.
        
        **Must** be called before anything else!
        """
        self.resources = {}
        self.cacheGroups = {}
        self.cacheCount = {}
    
    # Resource primitives #
    
    def addResource(self, key, resource):
        """
        Adds a resource to the manager.
        
        A ``KeyError`` is raised if a resource of the same key already exists.
        """
        if key not in self.resources:
            self.resources[key] = resource
        else:
            raise KeyError(key)
    
    def getResource(self, key):
        """
        Retrieves a resource from the manager.
        
        A ``KeyError`` is raised if no resource exists with that key.
        """
        if key in self.resources:
            return self.resources[key]
        else:
            raise KeyError(key)
    
    def removeResource(self, key):
        """
        Removes a resource from the manager.
        
        A ``KeyError`` is raised if no resource exists with that key.
        """
        if key in self.resources:
            del self.resources[key]
        else:
            raise KeyError(key)
    
    # Resource operations #
    
    def cacheResource(self, key, force=False):
        """
        Caches the resource.
        
        This increases the cache count of the resource, so it will not be
        uncached by resource groups.
        
        The ``force`` flag has the exact same meaning as the one in
        `Resource.createCache`.
        """
        self.getResource(key).createCache(force=force)
        try:
            self.cacheCount[cacheKey] += 1
        except KeyError:
            self.cacheCount[cacheKey] = 1
    
    def uncacheResource(self, key):
        """
        Destroys the resource's cache.
        
        This decreases the cache count of the resource, so it will not be
        uncached until all resource groups are uncached.
        """
        try:
            self.cacheCount[cacheKey] -= 1
        except KeyError:
            self.cacheCount[cacheKey] = 0
        if self.cacheCount[cacheKey] <= 0:
            self.getResource(key).destroyCache()
    
    def loadResource(self, key, *args, **kw):
        """
        Loads the resource with the given key.
        
        Any additional arguments are passed to the resource's `Resource.load`
        method.
        """
        return self.getResource(key).load(*args, **kw)
    
    # Cache group primitives #
    
    def addCacheGroup(self, key, resourceKeys):
        """
        Adds a cache group to the manager.
        
        A ``KeyError`` is raised if a cache group of the same key already
        exists.
        """
        if key not in self.cacheGroups:
            self.cacheGroups[key] = frozenset(resourceKeys)
        else:
            raise KeyError(key)
    
    def getCacheGroup(self, key):
        """
        Retrieves a cache group from the manager.
        
        A ``KeyError`` is raised if no cache group exists with that key.
        """
        if key in self.cacheGroups:
            return self.cacheGroups[key]
        else:
            raise KeyError(key)
    
    def removeCacheGroup(self, key):
        """
        Removes a cache group from the manager.
        
        A ``KeyError`` is raised if no cache group exists with that key.
        """
        if key in self.cacheGroups:
            del self.cacheGroups[key]
        else:
            raise KeyError(key)
    
    # Cache group operations #
    
    def cacheGroup(self, key, force=False):
        """
        Caches the resources in a cache group.
        
        The ``force`` flag has the exact same meaning as the one in
        `Resource.createCache`.
        """
        for cacheKey in self.getCacheGroup(key):
            self.cacheResource(key, force=force)
    
    def uncacheGroup(self, key):
        """
        Uncaches the resources in a cache group.
        
        Because multiple groups may reference the same resource, you should not
        depend on all of the resources being uncached.
        """
        for cacheKey in self.getCacheGroup(key):
            self.uncacheResource(key)

resman = ResourceManager()

class Resource(object):
    """Generic resource object."""
    def __init__(self, path):
        self.path = path
        self.cache = None
    
    def load(self):
        """
        Load the resource.
        
        The default implementation is not implemented, so it must be overridden
        in subclasses.  The return value should be something immediately usable,
        such as a ``pygame.Surface`` object.
        """
        raise NotImplementedError()
    
    def createCache(self, *args, **kw):
        """
        Creates a resource cache.
        
        The default implementation passes arguments to the `load` method and
        stores the result to the ``cache`` attribute.
        
        The ``force`` keyword will specify whether to refresh the cache if the
        cache already exists.
        """
        force = kw.pop('force', False)
        if force or self.cache is None:
            self.cache = self.load(*args, **kw)
    
    def destroyCache(self):
        """
        Destroys the resource cache.
        
        The default implementation sets the ``cache`` attribute to ``None``.
        """
        self.cache = None

class ImageResource(Resource):
    """Image resource loader."""
    def __init__(self, path, convert=True, alpha=True):
        """
        Initializes the resource.
        
        In addition to ``path``, there are two parameters, ``convert`` and
        ``alpha``. ``convert`` specifies whether the resource should be
        converted to the screen format after being loaded. ``alpha`` specifies
        whether alpha information should be preserved, but the flag is ignored
        if ``convert`` is ``False``.
        """
        super(ImageResource, self).__init__(path)
        self.convert = convert
        self.alpha = alpha
    
    def load(self):
        img = pygame.image.load(self.path)
        if self.convert:
            if self.alpha:
                return img.convert_alpha()
            else:
                return img.convert()
        else:
            return img

class AudioResource(Resource):
    """Encapsulates all audio resources."""
    pass

class SoundResource(AudioResource):
    """Sound resource loader."""
    def load(self):
        return pygame.mixer.Sound(self.path)

class MusicResource(AudioResource):
    """
    Music resource loader.
    
    The `load` method returns ``None``, as the loader loads the music into
    pygame's music mixer.
    """
    def load(self):
        pygame.mixer.music.load(self.path)
    
    def createCache(self):
        raise TypeError("Music doesn't support caching")
    
    def destroyCache(self):
        raise TypeError("Music doesn't support caching")
    