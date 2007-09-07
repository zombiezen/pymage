#!/usr/bin/env python
#
#   resman.py
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
Handles all resources

:Variables:
    resman : `ResourceManager`
        Global resource manager
"""

import warnings

import pygame

from pymage import states, vfs

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
    
    :IVariables:
        resources : dict
            Resources
        cacheGroups : dict
            Cache groups
        cacheCount : dict
            The number of cache references
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
        
        :Parameters:
            key : string
                Name of the resource
            resource : `Resource`
                Resource object
        :Raises KeyError: If a resource of the same key already exists.
        """
        if key not in self.resources:
            self.resources[key] = resource
        else:
            raise KeyError(key)
    
    def getResource(self, key):
        """
        Retrieves a resource from the manager.
        
        :Parameters:
            key : string
                Name of the resource
        :Raises KeyError: If no resource exists with that key.
        :Returns: The resource with the given key
        :ReturnType: `Resource`
        """
        if self.hasResource(key):
            return self.resources[key]
        else:
            raise KeyError(key)
    
    def hasResource(self, key):
        """
        Query the existence of the resource.
        
        :Parameters:
            key : string
                Name of the resource
        :Returns: Whether the manager has the key
        :ReturnType: bool
        """
        return key in self.resources
    
    def removeResource(self, key):
        """
        Removes a resource from the manager.
        
        :Parameters:
            key : string
                Name of the resource
        :Raises KeyError: If no resource exists with that key.
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
        
        :Parameters:
            key : string
                Name of the resource
            force : bool
                Whether to refresh the cache if the cache already exists
        :See: `Resource.createCache`
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
        
        :Parameters:
            key : string
                Name of the resource
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
        
        :Parameters:
            key : string
                Name of the resource
        """
        return self.getResource(key).get(*args, **kw)
    
    # Cache group primitives #
    
    def addCacheGroup(self, key, resource_keys):
        """
        Adds a cache group to the manager.
        
        :Parameters:
            key : string
                Name of the cache group
            resource_keys : list
                List of resource keys to cache
        :Raises KeyError: If a cache group of the same key already exists.
        """
        if key not in self.cacheGroups:
            self.cacheGroups[key] = frozenset(resource_keys)
        else:
            raise KeyError(key)
    
    def getCacheGroup(self, key):
        """
        Retrieves a cache group from the manager.
        
        :Parameters:
            key : string
                Name of the cache group
        :Raises KeyError: If no cache group exists with that key.
        :Returns: The cache group with the given key
        :ReturnType: frozenset
        """
        if self.hasCacheGroup(key):
            return self.cacheGroups[key]
        else:
            raise KeyError(key)
    
    def hasCacheGroup(self, key):
        """
        Query the existence of the cache group.
        
        :Parameters:
            key : string
                Name of the cache group
        :Returns: Whether the manager has the key
        :ReturnType: bool
        """
        return key in self.cacheGroups
    
    def removeCacheGroup(self, key):
        """
        Removes a cache group from the manager.
        
        :Parameters:
            key : string
                Name of the cache group
        :Raises KeyError: If no cache group exists with that key.
        """
        if key in self.cacheGroups:
            del self.cacheGroups[key]
        else:
            raise KeyError(key)
    
    # Cache group operations #
    
    def cacheGroup(self, key, force=False):
        """
        Caches the resources in a cache group.
        
        :Parameters:
            key : string
                Name of the cache group
            force : bool
                Whether to refresh the cache if the cache already exists
        :See: `Resource.createCache`
        """
        for cacheKey in self.getCacheGroup(key):
            self.cacheResource(cacheKey, force=force)
    
    def uncacheGroup(self, key):
        """
        Uncaches the resources in a cache group.
        
        Because multiple groups may reference the same resource, you should not
        depend on all of the resources being uncached.
        
        :Parameters:
            key : string
                Name of the resource
        """
        for cacheKey in self.getCacheGroup(key):
            self.uncacheResource(cacheKey)

resman = ResourceManager()

class Resource(object):
    """
    Generic resource object.
    
    :IVariables:
        path : string
            The path to the resource file
        cache
            The resource's cache (``None`` if there isn't one)
    """
    def __init__(self, path):
        """
        Initializes the resource.
        
        :Parameters:
            path : string
                The path to the resource file
        """
        self.__path = vfs.Path(path)
        self.cache = None
    
    def load(self):
        """
        Load the resource.
        
        The default implementation is not implemented, so it must be overridden
        in subclasses.  The return value should be something immediately usable,
        such as a ``pygame.Surface`` object.
        
        This is usually not called directly, instead, see the `get` method.
        
        :Returns: The resource's data
        """
        raise NotImplementedError()
    
    def get(self, *args, **kw):
        """
        Get the resource's content.
        
        The cache is returned, if it exists.  Otherwise, the resource is loaded,
        but no cache is saved.
        
        Any additional arguments are passed along to the `load` method.
        
        :Returns: The resource's data
        """
        if self.hasCache():
            return self.cache
        else:
            return self.load(*args, **kw)
    
    def createCache(self, *args, **kw):
        """
        Creates a resource cache.
        
        The default implementation passes arguments to the `load` method and
        stores the result to the `cache` attribute.
        
        :Keywords:
            force : bool
                Whether to refresh the cache if the cache already exists.
        """
        force = kw.pop('force', False)
        if force or self.cache is None:
            self.cache = self.load(*args, **kw)
    
    def hasCache(self):
        """
        Returns ``True`` if the resource has a cache.
        
        :Returns: Whether the resource has a cache
        :ReturnType: bool
        """
        return self.cache is not None
    
    def destroyCache(self):
        """
        Destroys the resource cache.
        
        The default implementation sets the `cache` attribute to ``None``.
        """
        self.cache = None
    
    def openFile(self, mode='r', buffering=None):
        """
        Opens a file object to the resource's path.
        
        :Parameters:
            mode : str
                The mode flag (same as built-in ``open`` call)
            buffering : int
                The buffering mode (same as built-in ``open`` call)
        :Returns: A file-like object representing that file
        :ReturnType: file
        """
        game = states.Game.getGame()
        if game is not None:
            return game.filesystem.open(self.__path, mode, buffering)
        else:
            if buffering is None:
                return open(str(self.__path), mode)
            else:
                return open(str(self.__path), mode, buffering)
    
    def getPath(self):
        """
        Resolves the resource's physical path.
        
        You can also use the `path` property.
        
        :Raises TypeError: If resolving is impossible
        :Returns: The physical file path
        :ReturnType: str
        """
        game = states.Game.getGame()
        if game is not None:
            return game.filesystem.resolve(self.__path)
        else:
            return str(self.__path)
    
    def setPath(self, newPath, **kw):
        """
        Changes the resource's abstract path.
        
        You can also use the `path` property.
        
        :Parameters:
            newPath : str or list
                The new path for the resource
        :Keywords:
            absolute : bool
                Whether the path is absolute
            directory : bool
                Whether the path is a directory
        """
        self.__path = Path(newPath, **kw)
    
    path = property(getPath, setPath,
                    doc="The path to the resource file")

class ImageResource(Resource):
    """
    Image resource loader.
    
    :IVariables:
        convert : bool
            Whether to convert to screen format after loading
        alpha : bool
            Whether alpha information should be preserved.  This is ignored if
            `convert` is ``False``.
    """
    def __init__(self, path, convert=True, alpha=True):
        """
        Initializes the resource.
    
        :IVariables:
            path : string
                Path to the resource file
        :Keywords:
            convert : bool
                Whether to convert to screen format after loading
            alpha : bool
                Whether alpha information should be preserved.  This is ignored
                if convert is ``False``.
        """
        super(ImageResource, self).__init__(path)
        self.convert = convert
        self.alpha = alpha
    
    def load(self):
        """
        Load the image.
        
        :Returns: The surface of the image
        :ReturnType: ``pygame.Surface``
        """
        img = pygame.image.load(self.openFile('rb'))
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
        """
        Load the sound.
        
        :Returns: The sound object
        :ReturnType: ``pygame.mixer.Sound``
        """
        return pygame.mixer.Sound(self.openFile('rb'))

class MusicResource(AudioResource):
    """Music resource loader."""
    def load(self):
        """
        Load the music into the Pygame music mixer.
        
        :Returns: ``None``
        """
        pygame.mixer.music.load(self.path)
    
    def createCache(self, *args, **kw):
        """Music doesn't support caching."""
        raise TypeError("Music doesn't support caching")
    
    def destroyCache(self):
        """Music doesn't support caching."""
        raise TypeError("Music doesn't support caching")

class Submanager(object):
    """
    Slave resource manager.
    
    Submanagers load resources from a central resource manager, but only deal
    with certain types.  They cannot modify the resources, only control their
    loading and caching.
    
    :CVariables:
        resourceType : `Resource` subclass
            The type of resource the submanager will load
    :IVariables:
        manager : `ResourceManager`
            The resource manager to use
    """
    resourceType = Resource
    
    def __init__(self, manager=None):
        """
        Initializes the submanager.
        
        :Parameters:
            manager : `ResourceManager`
                The resource manager to use.  Default is `pymage.resman.resman`.
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
        
        :Parameters:
            tag : string
                The key to add
            defaultPath : string
                The path of the key
        """
        warnings.warn("prepare is deprecated; use ResourceManager.addResource.",
                      DeprecationWarning,
                      stacklevel=2)
        if defaultPath is None:
            defaultPath = tag
        resource = self.resourceType(defaultPath)
        self.manager.addResource(tag, resource)
    
    def cache(self, key, force=False):
        """
        Cache the resource and return the resource's content.
        
        :Parameters:
            key : string
                The resource's key
            force : bool
                Whether to refresh the cache if the cache already exists.
        :Returns: The resource's data
        :Raises KeyError: If the resource doesn't exist or isn't of the correct
                          type
        :See: `Resource.createCache`
        """
        resource = self.manager.getResource(key)
        if isinstance(resource, self.resourceType):
            self.manager.cacheResource(key, force)
            return self.manager.loadResource(key)
        else:
            raise KeyError(key)
    
    def uncache(self, key):
        """
        Uncache the resource.
        
        :Parameters:
            key : string
                The resource's key
        :Raises KeyError: If the resource doesn't exist or isn't of the correct
                          type
        :See: `Resource.destroyCache`
        """
        resource = self.manager.getResource(key)
        if isinstance(resource, self.resourceType):
            self.manager.uncacheResource(key)
        else:
            raise KeyError(key)
    
    def load(self, key, *args, **kw):
        """
        Retreive's a resource's content.
        
        Any additional arguments are passed to `Resource.get`.
        
        :Parameters:
            key : string
                The resource's key
        :Raises KeyError: If the resource doesn't exist or isn't of the correct
                          type
        :See: `Resource.get`
        """
        resource = self.manager.getResource(key)
        if isinstance(resource, self.resourceType):
            return self.manager.loadResource(key, *args, **kw)
        else:
            raise KeyError(key)
    