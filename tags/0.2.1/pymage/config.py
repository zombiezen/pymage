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
    """Warning emitted when odd game site constructs are used."""
    pass

## CONFIG PARSER ##

class CaseConfigParser(ConfigParser):
    """A ``ConfigParser`` that is case-sensitive."""
    def optionxform(self, optstr):
        """Return the string in the same case."""
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
    for configFile in args:
        close = False
        if isinstance(configFile, basestring):
            # Open strings as paths
            path = os.path.normpath(os.path.expanduser(configFile))
            if os.path.exists(path):
                configFile = open(path)
            else:
                continue
            close = True
        parser.readfp(configFile)
        if close:
            configFile.close()
    # Assemble dictionary
    configDict = {}
    for section in parser.sections():
        sectionDict = {}
        for option in parser.options(section):
            value = parser.get(section, option)
            if convertValues:   # Interpret values
                value = _getValue(value)
            sectionDict[option] = value
        configDict[section] = sectionDict
    return configDict

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

def _getValue(value_string):
    """Retrieves a value from a ``ConfigParser`` string."""
    boolLiterals = {'false': False,
                    'no': False,
                    'off': False,
                    'true': True,
                    'yes': True,
                    'on': True,}
    if value_string.isdigit():
        # Integer
        return int(value_string)
    elif value_string.lower() in boolLiterals:
        # Boolean
        return boolLiterals[value_string.lower()]
    elif _isFloat(value_string):
        # Float
        return float(value_string)
    else:
        # String
        return str(value_string)

def _isFloat(value_string):
    """
    Returns whether the string is a ``float``.
    
    The format for a float is::
    
        int[.[fraction]]
    """
    if value_string.isdigit():
        # int
        return True
    elif value_string.count('.') == 1:
        # has a decimal point
        value_string = value_string.replace('.', '')
        if value_string.isdigit():
            # int[.[fraction]]
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

def setup(site='gamesite.xml', *config_files, **kw):
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
    config = _getSiteConfig(doc, config_files)
    # Load configuration
    if configSound:
        _processSoundOptions(config)
    if configMusic:
        _processMusicOptions(config)
    # Process resources
    _processGameSite(doc, config)
    # Return configuration dictionary
    return config

def _getSiteConfig(doc, config_files):
    """
    Find the full list of configuration files.
    
    The configuration files passed in are put first in the list, so the ones
    specified in the game site file take precedence.
    """
    siteConfigs = []
    for child in doc.documentElement.childNodes:
        if (child.nodeType == minidom.Node.ELEMENT_NODE and
            child.tagName == 'config-file'):
            siteConfigs.append(_getText(child))
    config_files = list(config_files) + list(siteConfigs)
    return load(*config_files)

def _processSoundOptions(config):
    """Configure the sound manager with the default configuration keys."""
    sound.sound.shouldPlay = bool(getOption(config, 'sound', 'play', True))
    sound.sound.volume = float(getOption(config, 'sound', 'volume', 1.0))

def _processMusicOptions(config):
    """Configure the music manager with the default configuration keys."""
    sound.music.shouldPlay = bool(getOption(config, 'music', 'play', True))
    sound.music.volume = bool(getOption(config, 'music', 'volume', 0.5))
    sound.music.loop = bool(getOption(config, 'music', 'loop', True))

def _processGameSite(doc, config):
    """Run through game site file and pull out resources."""
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
    """
    Handle a basic resource (i.e. images, sound effects, and custom resources).
    """
    attr = _attributes(elem, include_ns=False, ascii=True)
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
    """Handle a playlist element."""
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
                resman.addResource(musicKey, resman.MusicResource(musicPath))
                playlistKeys.append(musicKey)
            elif sub.tagName == 'music':
                # New-school music reference/declaration approach
                if sub.hasAttribute('ref'):
                    musicKey = sub.getAttribute('ref')
                else:
                    musicKey = _handlePrimitive(sub, config)
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
    """Handle a group element (a cache group)."""
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
                resourceKey = _handlePrimitive(sub, config)
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
    """
    Retrieve text from a DOM node, stripping indents, if asked.
    
    This function does honor the ``xml:space`` attribute, and if
    ``xml:space="preserve"`` is specified, it takes precendence over the
    ``post`` argument.
    """
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
    """Returns the first child with the given name, or ``None`` if not found."""
    for child in elem.childNodes:
        if (child.nodeType == minidom.Node.ELEMENT_NODE and
            child.tagName == name):
            return child
    else:
        return None

def _attributes(elem, include_ns=True, ascii=False):
    """
    Retrieves the attributes of a DOM node as a dictionary.
    
    If ``include_ns`` is ``True``, then attributes with a namespace will be
    discarded.  If ``ascii`` is ``True``, then the attribute names are converted
    to ASCII, but if they are unable to do so, the attribute is discarded.
    """
    nodemap = elem.attributes
    attrDict = {}
    for index in xrange(nodemap.length):
        attr = nodemap.item(index)
        if not include_ns and attr.prefix:
            continue
        name = attr.localName
        if ascii:
            try:
                name = str(name)
            except UnicodeError:
                continue
        attrDict[name] = attr.value
    return attrDict