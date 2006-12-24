#!/usr/bin/env python
#
#   config.py
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
        <playlist id="SamplePlaylist">
            <section>playlists</section>
            <option>sample</option>
            <path>music/song1.wav</path>
            <path>music/song2.wav</path>
        </playlist>
        
        <!-- Specify additional configuration files. -->
        <config-file>userconfig.ini</config-file>
    </game-site>
"""

from ConfigParser import ConfigParser
import os
from textwrap import dedent
from xml.dom import minidom

from sound import SoundManager, MusicManager
from sprites import ImageManager

__author__ = 'Ross Light'
__date__ = 'August 10, 2006'
__all__ = ['load',
           'save',
           'getOption',
           'setOption',
           'setup']
__docformat__ = 'reStructuredText'

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
                value = getValue(value)
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

def getValue(s):
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
    elif isFloat(s):                # Float
        return float(s)
    else:                           # String
        return str(s)

def isFloat(s):
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

def setup(site='gamesite.xml', *configFiles):
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
    """
    images, sounds, playlists, siteConfigs = parseGameSite(site)
    configFiles = list(configFiles) + list(siteConfigs)
    config = load(*configFiles)
    ImageManager.setup()
    SoundManager.setup(bool(getOption(config, 'sound', 'play', True)),
                       float(getOption(config, 'sound', 'volume', 1.0)),)
    MusicManager.setup(bool(getOption(config, 'music', 'play', True)),
                       float(getOption(config, 'music', 'volume', 0.5)),
                       bool(getOption(config, 'music', 'loop', True)),)
    # Set up images
    for tag, section, option, path in images:
        if option is None:
            # Using default path
            ImageManager.prepare(tag, path)
        else:
            # Using specified section/option
            if section is None:
                section = 'sprites'
            ImageManager.prepare(tag, getOption(config, section, option, path))
    # Set up sounds
    for tag, section, option, path in sounds:
        if option is None:
            # Using default path
            SoundManager.prepare(tag, path)
        else:
            # Using specified section/option
            if section is None:
                section = 'sound'
            SoundManager.prepare(tag, getOption(config, section, option, path))
    # Set up playlists
    for tag, section, option, paths in playlists:
        if option is None:
            # Using default path
            MusicManager.prepare(tag, paths)
        else:
            # Using specified section/option
            if section is None:
                section = 'music'
            oldPaths = paths
            paths = getOption(config, section, option, paths)
            if paths is not oldPaths:
                # Found the option successfully
                paths = paths.split(',')
            del oldPaths
            MusicManager.prepare(tag, paths)
    # Return config dictionary
    return config

def parseGameSite(f):
    doc = minidom.parse(f)
    images = []
    sounds = []
    playlists = []
    configs = []
    for child in doc.documentElement.childNodes:
        if child.nodeType == minidom.Node.ELEMENT_NODE:
            if child.tagName == 'image':
                images.append([child.getAttribute('id'),
                               getText(childNamed(child, 'section')),
                               getText(childNamed(child, 'option')),
                               getText(childNamed(child, 'path')),])
            elif child.tagName == 'sound':
                sounds.append([child.getAttribute('id'),
                               getText(childNamed(child, 'section')),
                               getText(childNamed(child, 'option')),
                               getText(childNamed(child, 'path')),])
            elif child.tagName == 'playlist':
                tag = child.getAttribute('id')
                section = getText(childNamed(child, 'section'))
                option = getText(childNamed(child, 'option'))
                paths = [getText(sub) for sub in child.childNodes if
                         sub.nodeType == minidom.Node.ELEMENT_NODE and
                         sub.tagName == 'path']
                playlists.append([tag, section, option, paths])
            elif child.tagName == 'config-file':
                configs.append(getText(child))
    return images, sounds, playlists, configs

def getText(elem, post=True):
    if elem is None:
        return None
    text = ''
    for child in elem.childNodes:
        if child.nodeType == minidom.Node.TEXT_NODE:
            text += child.wholeText
    if post:
        text = dedent(text)
        if text.startswith('\n'):
            text = text[1:]
            if text.endswith('\n'):
                text = text[:-1]
    return text

def childNamed(elem, name):
    for child in elem.childNodes:
        if (child.nodeType == minidom.Node.ELEMENT_NODE and
            child.tagName == name):
            return child
    else:
        return None
