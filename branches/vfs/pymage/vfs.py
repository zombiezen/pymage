#!/usr/bin/env python
#
#   vfs.py
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

"""Virtual file system abstraction"""

import os

import zope.interface

__author__ = 'Ross Light'
__date__ = 'August 30, 2007'
__docformat__ = 'reStructuredText'
__all__ = ['IFilesystem',
           'Path',
           'PhysicalFilesystem',]

class IFilesystem(zope.interface.Interface):
    def resolve(path):
        """
        Resolves the abstract path to a physical one.
        
        :Parameters:
            path : `Path` or string
                The abstract path to resolve
        :Raises TypeError: If resolving is impossible
        :Returns: The physical file path
        :ReturnType: str
        """
    
    def open(path, mode='r', buffering=None):
        """
        Opens a file object to the abstract path.
        
        :Parameters:
            path : `Path` or string
                The abstract path to open
            mode : str
                The mode flag (same as built-in ``open`` call)
            buffering : int
                The buffering mode (same as built-in ``open`` call)
        :Returns: A file or file-like object representing that file
        :ReturnType: file
        """
    
    def listdir(path):
        """
        Lists the children of a directory.
        
        :Parameters:
            path : `Path` or string
                The abstract path to the directory to list
        :Returns: A list of subpaths
        :ReturnType: list of `Path` objects
        """
    
    def exists(path):
        """
        Determines whether the path exists.
        
        :Parameters:
            path : `Path` or string
                The abstract path to check
        :ReturnType: bool
        """
    
    def isdir(path):
        """
        Determines whether the path is a directory.
        
        :Parameters:
            path : `Path` or string
                The abstract path to check
        :ReturnType: bool
        """
    
    def isfile(path):
        """
        Determines whether the path is a file.
        
        :Parameters:
            path : `Path` or string
                The abstract path to check
        :ReturnType: bool
        """

class Path(object):
    """
    A POSIX path conforming object.
    
    This is used to standardize paths across systems by using the POSIX path
    conventions.  Paths are split up into components, and are automatically
    normalized.
    
    :CVariables:
        sep : str
            Separator for string-based paths
        curdir : str
            Current directory indicator for string-based paths
        pardir : str
            Parent directory indicator for string-based paths
    :IVariables:
        components : tuple
            The components of the path
        absolute : bool
            Whether the path is absolute
        directory : bool
            Whether the path refers to a directory
    """
    
    sep = '/'
    curdir = '.'
    pardir = '..'
    
    def __init__(self,
                 path=[],
                 absolute=False,
                 directory=False):
        """
        Create a path.
        
        :Parameters:
            path
                The method of creation is dependent on what type of object this
                is.  If it is a:
                * `Path` object, then a copy is created.
                * string, then the path is parsed from the string.
                * sequence, then the path's components are constructed from the
                  members of the sequence and the keywords specify what kind of
                  path it is.
        :Keywords:
            absolute : bool
                Whether the path is absolute (i.e. has a leading slash)
            directory : bool
                Whether the path is a directory (i.e. has a trailing slash)
        """
        if isinstance(path, Path):          # Copy initialization
            components = path.components
            self.absolute = path.absolute
            self.directory = path.directory
        elif isinstance(path, basestring):  # Initialization from string
            # Determine absoluteness
            if path.startswith(self.sep):
                self.absolute = True
                path = path[len(self.sep):]
            else:
                self.absolute = False
            # Determine directory
            if path.endswith(self.sep):
                self.directory = True
                path = path[:-len(self.sep)]
            else:
                self.directory = False
            # Split components
            components = path.split(self.sep)
        else:                               # Initialization from sequence
            components = path
            self.absolute = bool(absolute)
            self.directory = bool(directory)
        self.components = tuple(self._normpath(components, self.absolute))
    
    @classmethod
    def _normpath(cls, components, absolute):
        """
        Normalize the path.
        
        This involves removing empty components and resolving immediately
        solvable parent references (e.g. "foo/../bar" turns into "bar", but
        "../foo/bar" remains the same).
        """
        # Do immediate path cleaning
        result = []
        for component in components:
            if cls.sep in component:
                raise ValueError("Separators are not allowed inside components")
            elif component and component != cls.curdir:
                result.append(component)
        # Remove any fixable parent directory issues
        startIndex = 0
        while True:
            try:
                parentIndex = result.index(cls.pardir, startIndex)
            except ValueError:
                break
            else:
                previousIndex = parentIndex - 1
                if previousIndex < startIndex:
                    startIndex += 1
                else:
                    del result[parentIndex]
                    del result[previousIndex]
        # Remove any leading parent directories if we are absolute
        if absolute:
            while result and result[0] == cls.pardir:
                del result[0]
        # Return result
        return result
    
    # Public API
    
    def relativePath(self, other):
        """
        Evaluate a path as relative to the caller.
        
        >>> path1 = Path('/home/python/')
        >>> path2 = Path('spam/eggs')
        >>> path1.relativePath(path2)
        Path(['home', 'python', 'spam', 'eggs'], absolute=True)
        >>> path2.relativePath('hello')
        Path(['spam', 'hello'])
        
        :Parameters:
            other : `Path`
                The path to resolve, relative to self
        :Returns: The resolved path
        :ReturnType: `Path`
        """
        otherPath = Path(other)
        if otherPath.absolute:
            return otherPath
        elif self.directory:
            return self + otherPath
        else:
            return self[:-1] + otherPath
    
    def convert(self, **kw):
        """
        Convert path to a different type.
        
        This doesn't affect the components, only the type of path.
        
        :Keywords:
            absolute : bool
                Whether the new path should be absolute
            directory : bool
                Whether the new path should be a directory
        :Returns: The converted path
        :ReturnType: `Path`
        """
        parameters = {'absolute': self.absolute,
                      'directory': self.directory,}
        parameters.update(kw)
        return Path(self.components, **parameters)
    
    # String representation
    
    def __repr__(self):
        result = "Path(%r" % list(self.components)
        if self.absolute:
            result += ", absolute=%r" % (self.absolute)
        if self.directory:
            result += ", directory=%r" % (self.directory)
        result += ")"
        return result
    
    def __str__(self):
        result = self.sep.join(self.components)
        if self.absolute:
            result = self.sep + result
        if self.directory:
            result += self.sep
        return result
    
    # Operators
    
    def __add__(self, other):
        if isinstance(other, Path):
            return Path(self.components + other.components,
                        absolute=self.absolute,
                        directory=other.directory)
        elif isinstance(other, basestring):
            return self + Path(other)
        elif isinstance(other, (tuple, list)):
            return Path(self.components + tuple(other),
                        absolute=self.absolute)
        else:
            return NotImplemented
    
    def __radd__(self, other):
        if isinstance(other, basestring):
            return Path(other) + self
        elif isinstance(other, (tuple, list)):
            return Path(tuple(other) + self.components,
                        directory=self.directory)
        else:
            return NotImplemented
    
    def __len__(self):
        return len(self.components)
    
    def __contains__(self, item):
        return item in self.components
    
    def __iter__(self):
        return iter(self.components)
    
    def __getitem__(self, item):
        if isinstance(item, slice):
            pathLength = len(self.components)
            sliceRange = xrange(*item.indices(pathLength))
            absolute = bool(self.absolute and sliceRange[0] == 0)
            directory = bool(self.directory and
                             sliceRange[-1] == pathLength - 1)
            return Path(self.components[item],
                        absolute=absolute,
                        directory=directory)
        elif isinstance(item, (int, long)) or hasattr(item, '__index__'):
            return self.components[item]
        else:
            typeName = type(item).__name__
            raise TypeError("Index or slice expected (got %s)" % typeName)
    
    # Comparison
    
    def __hash__(self):
        return hash(str(self))
    
    def __eq__(self, other):
        if isinstance(other, Path):
            return (self.components == other.components and
                    self.absolute == other.absolute and
                    self.directory == other.directory)
        elif isinstance(other, basestring):
            return str(self) == other
        elif isinstance(other, (list, tuple)):
            return self.components == tuple(other)
        else:
            return NotImplemented
    
    def __ne__(self, other):
        if isinstance(other, Path):
            return (self.components != other.components or
                    self.absolute != other.absolute or
                    self.directory != other.directory)
        elif isinstance(other, basestring):
            return str(self) != other
        elif isinstance(other, (list, tuple)):
            return self.components != tuple(other)
        else:
            return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, Path):
            if self.absolute and not other.absolute:
                return True
            result = cmp(self.components, other.components)
            if result == 1:
                return True
            elif result == 0:
                return bool(self.directory and not other.directory)
            else:
                return False
        elif isinstance(other, basestring):
            return bool(str(self) > other)
        elif isinstance(other, (list, tuple)):
            return self.components > tuple(other)
        else:
            return NotImplemented
    
    def __lt__(self, other):
        if isinstance(other, Path):
            if not self.absolute and other.absolute:
                return True
            result = cmp(self.components, other.components)
            if result == -1:
                return True
            elif result == 0:
                return bool(not self.directory and other.directory)
            else:
                return False
        elif isinstance(other, basestring):
            return bool(str(self) < other)
        elif isinstance(other, (list, tuple)):
            return self.components < tuple(other)
        else:
            return NotImplemented

class PhysicalFilesystem(object):
    zope.interface.implements(IFilesystem)
    
    def __init__(self, root):
        self.root = root
    
    @staticmethod
    def _abspath(path):
        if not isinstance(path, Path):
            path = Path(path)
        return path.convert(absolute=True)
    
    def resolve(self, path):
        return os.path.join(self.root, *self._abspath(path).components)
    
    def open(self, path, mode='r', buffering=None):
        if buffering is None:
            return open(self.resolve(path), mode)
        else:
            return open(self.resolve(path), mode, buffering)
    
    def listdir(self, path):
        path = self._abspath(path).convert(directory=True)
        result = []
        for name in os.listdir(self.resolve(path)):
            subpath = path.relativePath(name)
            if os.path.isdir(self.resolve(subpath)):
                subpath = subpath.convert(directory=True)
            result.append(subpath)
        result.sort()
        return result
    
    def exists(self, path):
        return os.path.exists(self.resolve(path))
    
    def isdir(self, path):
        return os.path.isdir(self.resolve(path))
    
    def isfile(self, path):
        return os.path.isfile(self.resolve(path))
