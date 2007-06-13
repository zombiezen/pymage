#!/usr/bin/env python
#
#   resman.py
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

"""Handles all resources"""

import warnings

import pygame

__author__ = 'Ross Light'
__date__ = 'February 19, 2007'
__all__ = ['ResourceManager',
           'resman',
           'Resource',
           'ImageResource',
           'AudioResource',
           'SoundResource',
           'MusicResource',
           'Submanager',]
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
        self.resources = {}
        self.cacheGroups = {}
        self.cacheCount = {}
    
    def cleanup(self):
        """Manually destroy all resources."""
        for key in self.cacheCount:
            self.getResource(key).destroyCache()
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
        if self.hasResource(key):
            return self.resources[key]
        else:
            raise KeyError(key)
    
    def hasResource(self, key):
        """Query the existence of the resource."""
        return key in self.resources
    
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
            self.cacheCount[key] += 1
        except KeyError:
            self.cacheCount[key] = 1
    
    def uncacheResource(self, key):
        """
        Destroys the resource's cache.
        
        This decreases the cache count of the resource, so it will not be
        uncached until all resource groups are uncached.
        """
        try:
            self.cacheCount[key] -= 1
        except KeyError:
            self.cacheCount[key] = 0
        if self.cacheCount[key] <= 0:
            self.getResource(key).destroyCache()
    
    def loadResource(self, key, *args, **kw):
        """
        Loads the resource with the given key.
        
        Any additional arguments are passed to the resource's `Resource.get`
        method.
        """
        return self.getResource(key).get(*args, **kw)
    
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
        if self.hasCacheGroup(key):
            return self.cacheGroups[key]
        else:
            raise KeyError(key)
    
    def hasCacheGroup(self, key):
        """Query the existence of the cache group."""
        return key in self.cacheGroups
    
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
            self.cacheResource(cacheKey, force=force)
    
    def uncacheGroup(self, key):
        """
        Uncaches the resources in a cache group.
        
        Because multiple groups may reference the same resource, you should not
        depend on all of the resources being uncached.
        """
        for cacheKey in self.getCacheGroup(key):
            self.uncacheResource(cacheKey)

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
        
        This is usually not called directly, instead, see the `get` method.
        """
        raise NotImplementedError()
    
    def get(self, *args, **kw):
        """
        Get the resource's content.
        
        The cache is returned, if it exists.  Otherwise, the resource is loaded,
        but no cache is saved.
        
        Any additional arguments are passed along to the `load` method.
        """
        if self.hasCache():
            return self.cache
        else:
            return self.load(*args, **kw)
    
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
    
    def hasCache(self):
        """Returns ``True`` if the resource has a cache."""
        return self.cache is not None
    
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

class Submanager(object):
    """
    Slave resource manager.
    
    Submanagers load resources from a central resource manager, but only deal
    with certain types.  They cannot modify the resources, only control their
    loading and caching.
    """
    resourceType = Resource
    
    def __init__(self, manager=None):
        """
        Initializes the submanager.
        
        Default uses the master resource manager
        (i.e. ``pymage.resman.resman``).
        """
        if manager is None:
            manager = resman
        self.manager = manager
    
    def prepare(self, tag, defaultPath=None):
        """
        Declares a tag for later use.
        
        .. Warning::
           `prepare` is retained for compatibility reasons.  You should be using
           `ResourceManager.addResource` to add new resources.
        """
        warnings.warn("prepare is deprecated; use ResourceManager.addResource.",
                      DeprecationWarning,
                      stacklevel=2)
        if defaultPath is None:
            defaultPath = tag
        resource = self.resourceType(defaultPath)
        self.manager.addResource(tag, resource)
    
    def cache(self, key, force=False):
        """Cache the resource and return the resource's content."""
        resource = self.manager.getResource(key)
        if isinstance(resource, self.resourceType):
            self.manager.cacheResource(key)
            return self.manager.loadResource(key)
        else:
            raise KeyError(key)
    
    def uncache(self, key):
        """Uncache the resource."""
        resource = self.manager.getResource(key)
        if isinstance(resource, self.resourceType):
            self.manager.uncacheResource(key)
        else:
            raise KeyError(key)
    
    def load(self, key, *args, **kw):
        """Retreive's a resource's content."""
        resource = self.manager.getResource(key)
        if isinstance(resource, self.resourceType):
            return self.manager.loadResource(key, *args, **kw)
        else:
            raise KeyError(key)
    