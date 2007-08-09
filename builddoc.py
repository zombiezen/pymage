#!/usr/bin/env python
#
#   builddoc.py
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

"""Build API documentation with epydoc"""

import os
import posixpath
import sys
import tarfile
import zipfile

__author__ = 'Ross Light'
__date__ = 'July 27, 2007'

progname = os.path.basename(sys.argv[0])
outputDirFormat = 'pymage-api-%s'
eggInfoName = 'pymage.egg-info'
pkgInfoName = 'PKG-INFO'
versionSymbol = 'Version:'
projectURL = 'http://code.google.com/p/pymage/'

class ProgramError(Exception):
    pass

def create_tgz(directory, output):
    t = tarfile.open(output, 'w:gz')
    t.add(directory, os.path.basename(directory))
    t.close()

def create_zip(directory, output):
    def pack(archive, paths, archivePath=None):
        for path in paths:
            if archivePath is None:
                archivePath = os.path.basename(path)
            if os.path.isdir(path):
                for entry in os.listdir(path):
                    pack(archive,
                         [os.path.join(path, entry)],
                         posixpath.join(archivePath, entry))
            else:
                archive.write(path, archivePath)
    z = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    pack(z, [directory])
    z.close()

try:
    # Ensure we have epydoc
    try:
        import epydoc
        from epydoc import log
        from epydoc.docbuilder import build_doc_index
        from epydoc.docwriter.html import HTMLWriter
    except ImportError:
        raise ProgramError("epydoc must be installed to build documentation")
    # Set up logging
    class BuildDocLogger(log.Logger):
        def __init__(self, threshold=log.WARNING):
            self.threshold = threshold
        
        def start_progress(self, header=None):
            if '-q' not in sys.argv[1:]:
                if header:
                    print "%s:" % header
                else:
                    print "epydoc task:"
        
        def progress(self, percent, message=''):
            if '-q' not in sys.argv[1:]:
                indent = ' ' * 2
                if message:
                    print indent + "epydoc: %s (%i%% completed)" % \
                                   (message, percent * 100)
                else:
                    print indent + "epydoc: %i%% completed" % (percent * 100)
        
        def end_progress(self):
            pass
        
        def log(self, level, message):
            if level >= self.threshold:
                print "%s: epydoc: %s" % (progname, message)
    logger = BuildDocLogger()
    log.register_logger(logger)
    # Make sure we're in the pymage source directory
    if not os.path.exists(os.path.join(os.getcwd(), eggInfoName)):
        raise ProgramError("Must be run in source directory")
    # Get version number
    pkgInfoFile = open(os.path.join(os.getcwd(), eggInfoName, pkgInfoName))
    try:
        for line in pkgInfoFile:
            if line.startswith(versionSymbol):
                version = line[len(versionSymbol):].strip()
                break
        else:
            raise ProgramError("Unable to find version number")
    finally:
        pkgInfoFile.close()
    # Create destination directory (if necessary)
    outputDir = os.path.join(os.getcwd(), outputDirFormat % version)
    if os.path.exists(outputDir):
        if not os.path.isdir(outputDir):
            raise ProgramError("Output path is not a directory")
    else:
        print "Creating '%s'..." % outputDir
        os.mkdir(outputDir)
    # Build documentation
    docIndex = build_doc_index(['pymage',])
    if docIndex is None:
        raise ProgramError("Documentation indexing failed")
    writer = HTMLWriter(docIndex,
                        prj_name='pymage',
                        prj_url=projectURL,
                        show_private=False,
                        show_imports=False,
                        include_source_code=False,)
    print "Writing documentation..."
    writer.write(outputDir)
    # Make archives
    print "Creating Tar-Gzip archive..."
    create_tgz(outputDir, (os.path.extsep).join([outputDir, 'tar', 'gz']))
    print "Creating Zip archive..."
    create_zip(outputDir, outputDir + os.path.extsep + 'zip')
except ProgramError, e:
    msg = str(e)
    msg = msg[0].lower() + msg[1:]
    print >> sys.stderr, "%s: %s" % (progname, str(e))
    sys.exit(1)
except Exception, e:
    print >> sys.stderr, "%s: internal error: %s" % (progname, str(e))
    sys.exit(-1)
else:
    sys.exit(0)
