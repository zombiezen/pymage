# Introduction #

pymage uses [setuptools](http://peak.telecommunity.com/DevCenter/setuptools) for its installation, so for most users, the installation is nearly painless.

# Requirements #

Recent versions of pymage (0.3.0 and newer) need [zope.interface](http://www.zope.org/Products/ZopeInterface).

## Optional Packages ##

  * [PyOpenGL](http://pyopengl.sourceforge.net/) (for 3D support)
  * [Twisted](http://twistedmatrix.com/) (for an asynchronous event loop)
  * [NumPy](http://numpy.scipy.org/) (for fast vectors)

# The easy\_install way #

If you have easy\_install on your system,  run ` easy_install pymage ` at your shell.

# The end-user way #

For users of the library without easy\_install, the procedure is usually the same regardless of whether you have setuptools installed.  However, if you do not have setuptools installed, the installation script will automatically install it for you (requires internet connection).

To install, download one of the recent source archives (i.e. pymage-0.3.0patch1.zip or pymage-0.3.0patch1.tar.gz) and unpack it.  Then, change into the directory and execute ` python setup.py install ` at your command line prompt.

# The developer's way #

Check out the trunk from Subversion, and run ` python setup.py develop ` inside the code's root directory.