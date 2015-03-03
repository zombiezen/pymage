# Introduction #

Starting with pymage version 0.2.0, a new and more extensible paradigm for resource-loading has been introduced: the global resource manager.  Unfortunately, this new system breaks compatibility with older versions of pymage.  This page documents how to fix older code and how to use the new system.

# Abstract #

## Resources ##

Every resource in your program has a key which uniquely identifies it across the program.  Using this key, you can load and manage the cache of the resource.  This resource could be anything from an image, a sound effect, or a project-specific resource, such as a map or an interface.  By default, pymage provides support for images, sound effects, and music.

## Caching ##

Each resource has a cache that can be created or destroyed.  The resource manager retains a cache count on each resource that starts at zero.  It is incremented every time a piece of code asks for a cache, and is decremented every time a piece of code asks to uncache the resource.  When the count is above zero, the resource manager caches the resource, but when it is zero or negative, the cache is destroyed.  This ensures the cache is retained even if no one is actively using it, but it forces you to manually uncache the resource.

Now some may argue that this is un-Pythonic, and is nearly as bad as manual garbage collection.  However, it is a necessary evil, since many games load resources into memory for the purpose of responsiveness, but not immediately use them (i.e. the resources are cached at the beginning of the level).  With that said, there is a mechanism for caching en masse.

## Cache Groups ##

Cache groups can be created that have a unique key (separate from the resource namespace).  Each cache group holds a set of resource keys that it is associated with.  When a cache group is cached, all of the resources inside the group increment their cache count.  Likewise, when a cache group is uncached, all of the resources inside the group decrement their cache count.

# Details #

The resource manager is accessed through the ` pymage.resman ` module.  The class ` ResourceManager ` handles all resources and the resources are represented by the abstract ` Resource ` class.  The global resource manager is accessed through the module variable ` pymage.resman.resman `.

## Creating a New Resource Type ##

To create a new resource type, you must subclass the ` pymage.resman.Resource ` class and override the ` load ` method.  For example:

```
class MyResource(pymage.resman.Resource):
    def load(self):
        f = open(self.path, 'rb')
        # Perform fancy I/O operations
        return someObject
```

## Sound, Music, and Images ##

The classic pymage ` SoundManager `, ` MusicManager `, and ` ImageManager ` still exist in the new system, but they now directly interface with the global resource manager and are no longer singleton classes.

The compatibility implications of this are:
  * You _must_ update all references to the manager classes to their new module variables:
    * ` pymage.sound.SoundManager ` > ` pymage.sound.sound `
    * ` pymage.sound.MusicManager ` > ` pymage.sound.music `
    * ` pymage.sprites.ImageManager ` > ` pymage.sprites.im `
  * You _should_ add resources by adding directly to the global resource manager (but if you just used the game site file, then you don't have to worry about this)
  * You _should_ change the ` get* ` method calls to ` load ` method calls (a standard part of the ` pymage.resman.Submanager ` API)

## Game Site File ##

With the new resource manager system, the game site configuration has been updated, too.  Most game site files should continue to work, and will transparently use the new resource manager paradigm.  However, some new features have been added.

### Custom Resource Types ###

You can now add custom elements to your game site file by subclassing ` Resource ` (see above), and registering them with the ` pymage.config.registerType ` function.  The function takes two arguments: the name of the custom tag and the resource class.  Any additional attributes found on the element in the game site file will be passed as keyword arguments to the class's initialization method.

### Manual Audio Configuration ###

The ` pymage.config.setup ` function now can take two optional keyword arguments: ` configSound ` and ` configMusic `.  These boolean arguments specify whether the music and sound volume should be automatically read from the configuration dictionary.  You could disable this to use an audio library different from SDL (OpenAL, perhaps?), or just to use different keys.

### Compatibility ###

Instead of using ` <path> ` elements, you should use ` <music> ` elements with a ` ref ` attribute that points to a music resource (i.e. another ` <music> ` element).  For the specifics, see the [API reference](http://code.google.com/p/pymage/downloads/detail?name=pymage-api-0.2.0.zip), but here is an excerpt from the game site file:

```
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
    <path>music/song2.wav</path> <!-- Still works, but deprecated -->
</playlist>
```