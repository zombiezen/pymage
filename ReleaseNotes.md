# Version 0.3.0patch1 #

  * Fixed fatal VFS config bug
  * Added game flag for not chdir-ing to game root
  * Fixed PackageResources to strip leading parents and turn relative

# Version 0.3.0 #

  * Added virtual file system, which supports:
    * Physical file system
    * [pkg\_resources](http://peak.telecommunity.com/DevCenter/PkgResources)
  * Fixed Numeric angle calculation bug
  * Fixed config.save section bug

# Version 0.2.2 #

  * Major documentation overhaul
  * Added global game instance retrieval
  * Upgraded to [LGPLv3](http://www.gnu.org/licenses/lgpl.html)
  * Added [Twisted](http://twistedmatrix.com/) support

# Version 0.2.1 #

  * Internal code clean up
  * Added timer groups
  * Fixed submanager force flag ignorance bug
  * Added list\*D methods to Vector

# Version 0.2.0 #

  * Added new master resource manager, which supports:
    * New resource types
    * Cache groups
  * **Code that used the old sound and music managers will no longer work**, see ResourceManager
  * Added configSound
  * Upgraded unit tests
  * Added fast vectors with transparent support for [Numeric Python](http://numpy.scipy.org/)
  * Added minimal [OpenGL](http://pyopengl.sourceforge.net/) support
  * Added end method to Game class

# Version 0.1.2 #

  * Fixed vector multiplication/division
  * Added demo directory
  * Added initial timer module
  * Added Menu class (for UI screens)
  * Added initial UI implementation (fairly adequate for a first implementation)
  * Added configuration-writing functions (save & setOption)
  * Added sprites.getImage function
  * Added initial documentation (very incomplete)
  * Rewrote documentation in ReST
  * Changed volume property into methods (properties don't work on classes)

# Version 0.1.1 #

  * Ported setup script to setuptools
  * Updated information in setup scripts.

# Version 0.1.0 #

  * First public release


