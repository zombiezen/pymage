#!/usr/bin/env python
#
#   config.py
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

"""
Provide configuration for your game.

The typical use of this module is to use the `setup` function and give set up
parameters.  From there, the module sets up the correct parts of the pymage
library.

This module is not strictly necessary, but pymage's reasoning is as follows:

Resources for the game should be loaded on an location-independent basis.
This provides abstraction and the ability for arbitrary file structure.
However, these files eventually need to be located, so the developer should
create a file (separate from the main code) that locates everything.  From
there, there may be a legitimate reason for the user to want to customize the
file locations (perhaps he/she wants the game resources to be on a separate hard
drive).  Therefore, a separate file is used to override the behavior of any
given installation of the game.  But since the user never touches the
developer's default game setup, any corrupt preferences can be corrected by
deleting the user configuration files.

Here is a sample gamesite.xml file::

    <?xml version="1.0"?>
    
    <!-- name is not necessary, but reserved for future use. -->
    <game-site name="Sample Game">
        <!-- Prepare an image in the ImageManager.
             The id attribute is used as the tag.
             The path element is required to find the file.
             The section and option elements specify how the path can be
             overriden in configuration files. -->
        <image id="SampleImage">
            <section>sprites</section>
            <option>sample</option>
            <path>img/sample.png</path>
        </image>
        
        <!-- Prepare a sound in the SoundManager.
             The id attribute is used as the tag.
             The path element is required to find the file.
             The section and option elements specify how the path can be
             overriden in configuration files. -->
        <sound id="SampleSound">
            <section>sounds</section>
            <option>sample</option>
            <path>sfx/sample.wav</path>
        </sound>
        
        <!-- Prepare a playlist in the MusicManager.
             The id attribute is used as the tag.
             The path element(s) are required to find the music file(s).
             The section and option elements specify how the playlist can be
             overriden in configuration files. -->
        <music id="song1">
            <path>music/song1.wav</path>
        </music>
        <playlist id="SamplePlaylist">
            <section>playlists</section>
            <option>sample</option>
            <music ref="song1"/>
            <path>music/song2.wav</path> <!-- Old way, still works -->
        </playlist>
        
        <!-- Prepare a cache group. -->
        <group id="SampleGroup">
            <section>groups</section>
            <option>sample</option>
            <image ref="SampleImage"/>
            <sound ref="SampleSound"/>
        </group>
        
        <!-- Specify additional configuration files. -->
        <config-file>userconfig.ini</config-file>
    </game-site>
"""

from ConfigParser import ConfigParser
import os
from textwrap import dedent
import warnings
from xml.dom import minidom

from pymage import resman
from pymage import sound

__author__ = 'Ross Light'
__date__ = 'August 10, 2006'
__all__ = ['GameSiteWarning',
           'load',
           'save',
           'getOption',
           'setOption',
           'registerType',
           'unregisterType',
           'setup',]
__docformat__ = 'reStructuredText'

# Globals
_gsPrims = {'resource': resman.Resource,
            'image': resman.ImageResource,
            'sound': resman.SoundResource,
            'music': resman.MusicResource,}

class GameSiteWarning(UserWarning):
    pass

## CONFIG PARSER ##

class CaseConfigParser(ConfigParser):
    """A ``ConfigParser`` that is case-sensitive."""
    def optionxform(self, optstr):
        return optstr

def load(*args, **kw):
    """
    Load a series of configuration files.
    
    This function returns a dictionary of values.  Any optional keyword values
    are used as variables.  The special keyword ``convert`` specifies whether
    the function should interpret the values as what they seem to be
    (e.g. ``float``, ``int``).  The default is ``True``.
    """
    # Retrieve convert keyword
    convertValues = kw.get('convert', True)
    try:
        del kw['convert']
    except KeyError:
        pass
    # Parse the files
    parser = CaseConfigParser(kw)
    for f in args:
        close = False
        if isinstance(f, basestring):
            # Open strings as paths
            path = os.path.normpath(os.path.expanduser(f))
            if os.path.exists(path):
                f = open(path)
            else:
                continue
            close = True
        parser.readfp(f)
        if close:
            f.close()
    # Assemble dictionary
    d = {}
    for section in parser.sections():
        sectDict = {}
        for option in parser.options(section):
            value = parser.get(section, option)
            if convertValues:   # Interpret values
                value = _getValue(value)
            sectDict[option] = value
        d[section] = sectDict
    return d

def save(config, configFile):
    """Saves a configuration dictionary to a file."""
    close = False
    parser = CaseConfigParser()
    for section, values in config.iteritems():
        for option, value in values.iteritems():
            parser.set(section, option, value)
    if isinstance(configFile, basestring):
        path = os.path.normpath(os.path.expanduser(configFile))
        configFile = open(path, 'w')
        close = True
    parser.write(configFile)
    if close:
        configFile.close()

def _getValue(s):
    """Retrieves a value from a ``ConfigParser`` string."""
    boolLiterals = {'false': False,
                    'no': False,
                    'off': False,
                    'true': True,
                    'yes': True,
                    'on': True,}
    if s.isdigit():                 # Integer
        return int(s)
    elif s.lower() in boolLiterals: # Boolean
        return boolLiterals[s.lower()]
    elif _isFloat(s):               # Float
        return float(s)
    else:                           # String
        return str(s)

def _isFloat(s):
    """
    Returns whether the string is a ``float``.
    
    The format for a float is::
    
        int[.[fraction]]
    """
    if s.isdigit():         # int
        return True
    if s.count('.') == 1:
        s = s.replace('.', '')
        if s.isdigit():     # int[.[fraction]]
            return True
        else:
            return False
    else:
        return False

def getOption(config, section, option, default=None):
    """Retrieves an option from the configuration dictionary."""
    try:
        section = config[section]
    except KeyError:
        return default
    else:
        return section.get(option, default)

def setOption(config, section, option, value):
    """Changes an option in the configuration dictionary."""
    section = config.setdefault(section, {})
    section[option] = value

## GAME SITE ##

def registerType(tag, factory):
    """
    Register a custom game site resource type.
    
    The ``tag`` argument is the name of the XML element, and ``factory`` is a
    callable that takes one argument: a path to the resource.  The ``factory``
    is typically the constructor of a `resman.Resource` subclass.
    """
    _gsPrims[tag] = factory

def unregisterType(tag):
    """Unregister a custom game site resource type."""
    del _gsPrims[tag]

def setup(site='gamesite.xml', *configFiles, **kw):
    """
    Sets up a game from the specified parameters and returns the configuration
    dictionary.
    
    The first argument is the game site file.  The game site file contains most
    of the setup information.  It specifies the resource IDs and where to find
    the configuration files.  It should only be modified by developers as the
    game is created.
    
    The additional arguments are program default configuration files.  These
    are parsed before any inside the game site file (therefore giving the site
    configuration files higher precedence).
    
    Additional keyword arguments can be specified. ``configSound`` specifies
    whether the sound manager volume is configured, and ``configMusic``
    specifies whether the music manager volume is configured.
    """
    # Get keyword arguments
    configSound = kw.pop('configSound', True)
    configMusic = kw.pop('configMusic', True)
    if kw:
        raise TypeError("Invalid keyword argument")
    # Parse game site file
    doc = minidom.parse(site)
    config = _getSiteConfig(doc, configFiles)
    # Load configuration
    if configSound:
        _processSoundOptions(config)
    if configMusic:
        _processMusicOptions(config)
    # Process resources
    _processGameSite(doc, config)
    # Return configuration dictionary
    return config

def _getSiteConfig(doc, configFiles):
    siteConfigs = []
    for child in doc.documentElement.childNodes:
        if (child.nodeType == minidom.Node.ELEMENT_NODE and
            child.tagName == 'config-file'):
            siteConfigs.append(_getText(child))
    configFiles = list(configFiles) + list(siteConfigs)
    return load(*configFiles)

def _processSoundOptions(config):
    sound.sound.shouldPlay = bool(getOption(config, 'sound', 'play', True))
    sound.sound.volume = float(getOption(config, 'sound', 'volume', 1.0))

def _processMusicOptions(config):
    sound.music.shouldPlay = bool(getOption(config, 'music', 'play', True))
    sound.music.volume = bool(getOption(config, 'music', 'volume', 0.5))
    sound.music.loop = bool(getOption(config, 'music', 'loop', True))

def _processGameSite(doc, config):
    configs = []
    handlers = {'playlist': _handlePlaylist,
                'group': _handleGroup,}
    handlers.update(dict.fromkeys(_gsPrims, _handlePrimitive))
    for child in doc.documentElement.childNodes:
        if (child.nodeType == minidom.Node.ELEMENT_NODE and
            child.tagName in handlers):
            # Call handler
            handler = handlers[child.tagName]
            handler(child, config)

def _handlePrimitive(elem, config):
    attr = _attributes(elem, ascii=True)
    pathChild = _childNamed(elem, 'path')
    if pathChild is None:
        warnings.warn("Primitive without a path", GameSiteWarning)
        return
    # Get ID
    try:
        key = attr.pop('id')
    except KeyError:
        pathChild = _childNamed(elem, 'path')
        if pathChild:
            key = _getText(pathChild)
        else:
            warnings.warn("Primitive without a key", GameSiteWarning)
            return
    # Get resource information
    resType = _gsPrims[elem.tagName]
    section = _getText(_childNamed(elem, 'section'))
    option = _getText(_childNamed(elem, 'option'))
    path = _getText(pathChild)
    # Create resource
    if section is not None and option is not None:
        path = getOption(config, section, option, path)
    resman.resman.addResource(key, resType(path, **attr))
    # Return key
    return key

def _handlePlaylist(elem, config):
    key = elem.getAttribute('id')
    section = _getText(_childNamed(elem, 'section'))
    option = _getText(_childNamed(elem, 'option'))
    playlistKeys = []
    # Get playlist keys
    for sub in elem.childNodes:
        if sub.nodeType == minidom.Node.ELEMENT_NODE:
            if sub.tagName == 'path':
                # Old-school path approach
                warnings.warn("%s using old path-based playlist" % (key),
                              GameSiteWarning)
                if sub.hasAttribute('id'):
                    musicKey = sub.getAttribute('id')
                    musicPath = _getText(sub)
                else:
                    musicKey = musicPath = _getText(sub)
                kw['resources'][musicKey] = \
                    (resman.MusicResource, None, None, musicPath)
                playlistKeys.append(musicKey)
            elif sub.tagName == 'music':
                # New-school music reference/declaration approach
                if sub.hasAttribute('ref'):
                    musicKey = sub.getAttribute('ref')
                else:
                    musicKey = _handlePrimitive(sub, **kw)
                playlistKeys.append(musicKey)
    # Create playlist
    if section is not None and option is not None:
        configKeys = getOption(config, section, option)
        if configKeys is not None:
            playlistKeys = configKeys.split(',')
    sound.music.addPlaylist(key, playlistKeys)
    # Return key
    return key

def _handleGroup(elem, config):
    key = elem.getAttribute('id')
    section = _getText(_childNamed(elem, 'section'))
    option = _getText(_childNamed(elem, 'option'))
    groupKeys = set()
    # Get group keys
    for sub in elem.childNodes:
        if (sub.nodeType == minidom.Node.ELEMENT_NODE and
            sub.tagName in _gsPrims):
            if sub.hasAttribute('ref'):
                resourceKey = sub.getAttribute('ref')
            else:
                resourceKey = _handlePrimitive(sub, **kw)
            groupKeys.add(resourceKey)
    # Create group
    if section is not None and option is not None:
        configKeys = getOption(config, section, option)
        if configKeys is not None:
            groupKeys = configKeys.split(',')
    resman.resman.addCacheGroup(key, groupKeys)
    # Return key
    return key

def _getText(elem, post=True):
    xmlNS = 'http://www.w3.org/XML/1998/namespace'
    if elem is None:
        return None
    text = ''
    for child in elem.childNodes:
        if child.nodeType == minidom.Node.TEXT_NODE:
            text += child.wholeText
    preserve = (elem.hasAttributeNS(xmlNS, 'space') and
                elem.getAttributeNS(xmlNS, 'space') == 'preserve')
    if post and not preserve:
        text = dedent(text)
        if text.startswith('\n'):
            text = text[1:]
            if text.endswith('\n'):
                text = text[:-1]
    return text

def _childNamed(elem, name):
    for child in elem.childNodes:
        if (child.nodeType == minidom.Node.ELEMENT_NODE and
            child.tagName == name):
            return child
    else:
        return None

def _attributes(elem, includeNS=False, ascii=False):
    nodemap = elem.attributes
    d = {}
    for index in xrange(nodemap.length):
        attr = nodemap.item(index)
        if not includeNS and attr.prefix:
            continue
        name = attr.localName
        if ascii:
            try:
                name = str(name)
            except UnicodeError:
                continue
        d[name] = attr.value
    return d
