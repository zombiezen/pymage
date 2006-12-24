#!/usr/bin/env python
#
#   ui.py
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

"""Game user interface"""

import weakref

import pygame
from pygame.locals import *

import sprites

__author__ = 'Ross Light'
__date__ = 'July 20, 2006'
__all__ = ['left_align',
           'center_align',
           'right_align',
           'Widget',
           'Container',
           'TextWidget',
           'ImageWidget',
           'CursorWidget',
           'ButtonState',
           'StretchState',
           'Button',
           'PushButton',]
__docformat__ = 'reStructuredText'

# Constants

left_align = 0
center_align = 1
right_align = 2

class Widget(object):
    def __init__(self,
                 parent=None,
                 rect=Rect(0, 0, 0, 0),
                 cache=False):
        self.__oldRect = None
        self.rect = rect
        self.__children = set()
        self.parent = parent
        self.__updates = [Rect(0, 0, self.rect.width, self.rect.height)]
        if cache:
            self.createCache()
        else:
            self.destroyCache()
        self.__active = False
    
    # Caching
    
    def createCache(self):
        """(Re)Creates a cache for the widget."""
        self.__cache = pygame.Surface(self.rect.size).convert_alpha()
        self.refresh()
    
    def destroyCache(self):
        """Destroys the widget's cache."""
        self.__cache = None
        self.refresh()
    
    def hasCache(self):
        """Returns whether the widget has a cache."""
        return bool(self.__cache is not None)
    
    # Child management
    
    def __len__(self):
        return len(self.__children)
    
    def __iter__(self):
        return iter(self.__children)
    
    def children(self):
        """Returns a list of all children."""
        return list(self.__children)
    
    def childTree(self, includeSelf=False, topdown=True):
        """
        Returns an iterator descending the entire child tree.
        
        ``includeSelf`` is a flag specifying whether the widget is included in
        the iterator.
        
        ``topdown`` is a flag specifying whether to go from widget to bottom
        or bottom to widget.
        """
        if includeSelf and topdown:
            yield self
        for child in self.__children:
            tree = child.childTree(includeSelf=True,
                                   topdown=topdown)
            for subchild in tree:
                yield subchild
        if includeSelf and not topdown:
            yield self
    
    def addChild(self, child):
        """Adds a child widget."""
        self.__children.add(child)
        child.parent = self
    
    def addChildren(self, children):
        """Adds children widgets."""
        self.__children.update(frozenset(children))
        for child in children:
            child.parent = self
    
    def removeChild(self, child):
        """Removes a child widget."""
        self.__children.remove(child)
        del child.parent
    
    def removeAllChildren(self):
        """Removes all child widgets."""
        children = list(self.__children)
        self.__children.clear()
        for child in children:
            del child.parent
    
    def _getParent(self):
        if self.__parent is None:
            return None
        else:
            parent = self.__parent()
            if parent is None:
                self.__parent = None
            return parent
    
    def _setParent(self, newParent):
        # Remove self from old parent
        self._delParent()
        # Add self to new parent
        if newParent is None:
            self.__parent = newParent
        else:
            if self not in newParent.children():
                newParent.addChild(self)
            self.__parent = weakref.ref(newParent)
    
    def _delParent(self):
        try:
            if self.__parent is not None:
                parent = self.__parent()
                if parent is not None and self in parent:
                    parent.removeChild(self)
        except AttributeError:
            pass
        self.__parent = None
    
    def _getRoot(self):
        widget = self
        while True:
            parent = widget.parent
            if parent is None:
                break
            widget = parent
        return widget
    
    parent = property(_getParent, _setParent, _delParent)
    root = property(_getRoot)
    
    # Event management
    
    def handle(self, event):
        """
        Handles a single event.
        
        Override to perform custom event-handling.  Return ``True`` if the event
        was handled successfully.
        """
        return False
    
    def processEvent(self, event):
        """
        Processes an event.
        
        The return value is whether the event was processed successfully.
        
        The event will start at a certain widget and traverse up the child
        hierarchy until the event is handled or the root is reached.  The
        starting widget is dependent on what the event type is:
        
        * If the event is a mouse event, the widget that the mouse is/was over.
        * Otherwise, the active widget.
        
        Do not override this method to perform event handling; instead, override
        the `handle` method.
        """
        if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
            tree = self.root.childTree(includeSelf=True,
                                       topdown=False)
            for child in tree:
                if child.screenRect().collidepoint(*event.pos):
                    widget = child
                    break
            else:
                widget = None
        else:
            widget = self.root.activeWidget()
        while widget is not None:
            if widget.handle(event):
                return True
            widget = widget.parent
        else:
            return False
    
    def canFocus(self):
        """
        Returns whether the widget can be focused.
        
        Default returns ``False``.
        """
        return False
    
    def focus(self, forceBlur=False, forceFocus=False):
        """
        Makes the widget the active one.
        
        Returns whether the focus was successful.
        
        You may extend this implementation to perform custom handling, but
        always call this implementation to actually focus the widget.
        """
        if forceFocus or self.canFocus():
            activeWidget = self.root.activeWidget()
            if activeWidget is None or activeWidget.blur(force=forceBlur):
                self.__active = True
                return True
            else:
                return False
        else:
            return False
    
    def canBlur(self):
        """
        Returns whether the widget can be blurred.
        
        Default returns ``True``.
        """
        return True
    
    def blur(self, force=False):
        """
        Makes the widget inactive.
        
        Returns whether the blur was successful.
        
        You may extend this implementation to perform custom handling, but
        always call this implementation to actually blur the widget.
        """
        if force or self.canBlur():
            self.__active = False
            return True
        else:
            return False
    
    def activeWidget(self):
        """
        Returns the current active widget, or ``None`` if there is not one.
        
        Be mindful that this only traverses from the receiver down.
        """
        for child in self.childTree(includeSelf=True):
            if child.isActive():
                return child
        else:
            return None
    
    def isActive(self):
        """Returns whether the widget is active."""
        return self.__active
    
    # Displaying
    
    def display(self, surface=None, origin=(0, 0)):
        """
        Display the widget on the given surface.
        
        The return value is a list of Rects that need to be updated.
        
        If no ``surface`` is given, the current display surface is used.
        
        If no ``origin`` is given, (0, 0) is used.  The origin should be in
        local space.
        
        You *shouldn't* have to override this method.  Instead, you should
        override the draw method.
        """
        screenUpdates = []
        if surface is None:
            surface = pygame.display.get_surface()
        # Add old bounds to screen updates
        if self.__oldRect != self.rect:
            if self.__oldRect is not None:
                screenUpdates.append(self.__oldRect.move(origin))
            self.rectChanged(self.__oldRect, Rect(self.rect))
            if self.hasCache():
                self.createCache()
            screenUpdates.append(self.rect.move(origin))
            self.__oldRect = Rect(self.rect)
        # Calculate dirty region
        if self.__updates:
            region = self.__updates[0].unionall(self.__updates[1:])
            del self.__updates[:]
        else:
            region = None
        # Draw self
        if self.hasCache():
            # Using cache
            drawSurf = self.__cache
            if region is not None:
                self.draw(drawSurf, region)
        else:
            # Not using cache
            drawSurf = pygame.Surface(self.rect.size).convert_alpha(surface)
            self.draw(drawSurf, self.bounds())
        surface.blit(drawSurf, self.rect.move(origin))
        # Determine screen updates
        if region is not None:
            screenUpdates.append(self.btlrect(region, origin))
        # Display children
        childOrigin = self.rect.move(origin).topleft
        for child in self.__children:
            screenUpdates.extend(child.display(surface, childOrigin))
        return screenUpdates
    
    def draw(self, surface, rect):
        """
        Performs the actual drawing.
        
        Default implementation clears the surface to a transparent color.
        """
        surface.fill((0, 0, 0, 0), rect)
    
    def refresh(self, rect=None):
        """
        Inform the widget that a given portion needs to be refreshed.
        
        If no rect is given, the entire widget will be refreshed.
        """
        if rect is None:
            rect = Rect(0, 0, self.rect.width, self.rect.height)
        self.__updates.append(Rect(rect))
    
    # Updating
    
    def update(self):
        """
        Updates the widget.
        
        Default implementation calls `update` on child widgets.
        """
        for child in self.__children:
            child.update()
    
    # Coordinates
    
    def stlrect(self, rect, origin=(0, 0)):
        """Converts from a screen rectangle to a local rectangle."""
        rect = Rect(rect)
        origin = self._localOrigin(origin)
        return rect.move(-origin[0], -origin[1])
    
    def stbrect(self, rect, origin=(0, 0)):
        """Converts from a screen rectangle to a bounds rectangle."""
        rect = Rect(rect)
        origin = self._boundsOrigin(origin)
        return rect.move(-origin[0], -origin[1])
    
    def ltsrect(self, rect, origin=(0, 0)):
        """Converts from a local rectangle to a screen rectangle."""
        rect = Rect(rect)
        origin = self._localOrigin(origin)
        return rect.move(origin[0], origin[1])
    
    def ltbrect(self, rect, origin=(0, 0)):
        """Converts from a local rectangle to a bounds rectangle."""
        rect = Rect(rect)
        origin = self.rect.topleft
        return rect.move(-origin[0], -origin[1])
    
    def btsrect(self, rect, origin=(0, 0)):
        """Converts from a bounds rectangle to a screen rectangle."""
        rect = Rect(rect)
        origin = self._boundsOrigin(origin)
        return rect.move(origin[0], origin[1])
    
    def btlrect(self, rect, origin=(0, 0)):
        """Converts from a bounds rectangle to a screen rectangle."""
        rect = Rect(rect)
        origin = self.rect.topleft
        return rect.move(origin[0], origin[1])
    
    def stlpoint(self, point, origin=(0, 0)):
        """Converts from a screen point to a local point."""
        origin = self._localOrigin(origin)
        return (point[0] - origin[0], point[1] - origin[1])
    
    def stbpoint(self, point, origin=(0, 0)):
        """Converts from a screen point to a bounds point."""
        origin = self._boundsOrigin(origin)
        return (point[0] - origin[0], point[1] - origin[1])
    
    def ltspoint(self, point, origin=(0, 0)):
        """Converts from a local point to a screen point."""
        origin = self._localOrigin(origin)
        return (point[0] + origin[0], point[1] + origin[1])
    
    def ltbpoint(self, point, origin=(0, 0)):
        """Converts from a local point to a bounds point."""
        origin = self.rect.topleft
        return (point[0] - origin[0], point[1] - origin[1])
    
    def btspoint(self, point, origin=(0, 0)):
        """Converts from a bounds point to a screen point."""
        origin = self._boundsOrigin(origin)
        return (point[0] + origin[0], point[1] + origin[1])
    
    def btlpoint(self, point, origin=(0, 0)):
        """Converts from a bounds point to a local point."""
        origin = self.rect.topleft
        return (point[0] + origin[0], point[1] + origin[1])
    
    def _localOrigin(self, origin=(0, 0)):
        """Returns the local origin as screen coordinates."""
        origin = self.screenRect(origin).topleft
        return (origin[0] - self.rect.x, origin[1] - self.rect.y)
    
    def _boundsOrigin(self, origin=(0, 0)):
        """Returns the bounds origin as screen coordinates."""
        return self.screenRect(origin).topleft
    
    def screenRect(self, origin=(0, 0)):
        """Calculates the screen rectangle."""
        rect = Rect(self.rect)
        parent = self.parent
        while parent is not None:
            rect.move_ip(parent.rect.topleft)
            parent = parent.parent
        rect.move_ip(origin)
        return rect
    
    def bounds(self):
        """Returns the rectangle that can be drawn in."""
        return Rect(0, 0, self.rect.width, self.rect.height)
    
    # Dynamic sizing
    
    def optimalSize(self):
        """
        Returns the optimal size of the widget.
        
        Default returns ``None``, but subclasses can override to return a value.
        """
        return None
    
    def pack(self, anchor=None):
        """
        Changes the widget's rect to the optimal size.
        
        If `optimalSize` returns None, this does nothing.
        
        ``anchor`` is a string specifying a corner/edge attribute name that will
        remain constant after the resize.  For best results, specify a corner
        (e.g. topleft).
        """
        if anchor is not None:
            anchorValue = getattr(self.rect, anchor)
        size = self.optimalSize()
        if size is not None:
            self.rect.size = size
            if anchor is not None:
                setattr(self.rect, anchor, anchorValue)
    
    def rectChanged(self, oldRect, newRect):
        """
        Hook method for the rectangle changing.
        
        This is called before `display` does any drawing.
        """
        pass
    
    def _getRect(self):
        return self.__rect
    
    def _setRect(self, newRect):
        self.__rect = Rect(newRect)
    
    rect = property(_getRect, _setRect)

class Container(Widget):
    def __init__(self,
                 border=0,
                 borderColor=(0, 0, 0, 255),
                 bgColor=(0, 0, 0, 0),
                 *args, **kw):
        super(Container, self).__init__(*args, **kw)
        self.border = border
        self.borderColor = borderColor
        self.bgColor = bgColor
    
    def draw(self, surface, rect):
        surface.fill(self.bgColor, rect)
        if self.border > 0:
            pygame.draw.rect(surface,
                             self.borderColor,
                             self.bounds(),
                             self.border)
    
    def optimalSize(self):
        childRects = [child.rect for child in self.children()]
        if childRects:
            allChildRect = childRects[0].union_all(childRects[1:])
            return (allChildRect.x + allChildRect.width,
                    allChildRect.y + allChildRect.height)
        else:
            return None

class TextWidget(Widget):
    fgColor = (0, 0, 0, 255)
    bgColor = (0, 0, 0, 0)
    antialias = True
    shadow = False
    shadowColor = (0, 0, 0, 128)
    
    def __init__(self, text='', font=None, *args, **kw):
        """
        Initializes a text widget.
        
        Three additional parameters can be specified via keyword arguments:
        
        - ``fgColor``: The color of the rendered text.  Default is black.
        - ``bgColor``: The background color of the text.  Default is clear.
        - ``antialias``: Whether to antialias.  Default is ``True``.
        - ``align``: How to align the text.  Default is `left_align`.
        - ``shadow``: Whether the text has a drop shadow.  Default is ``False``.
        - ``shadowColor``: The drop shadow's color.  Default is a
          half-transparent black.
        """
        # Get keyword options
        self.fgColor = kw.pop('fgColor', self.fgColor)
        self.bgColor = kw.pop('bgColor', self.bgColor)
        self.antialias = kw.pop('antialias', self.antialias)
        self.align = kw.pop('align', left_align)
        self.shadow = kw.pop('shadow', self.shadow)
        # Perform superclass initialization
        super(TextWidget, self).__init__(*args, **kw)
        # Perform initialization
        self.text = text
        if font is None:
            font = pygame.font.Font(None, 14)
        self.font = font
    
    def draw(self, surface, rect):
        # Render text
        surface.fill(self.bgColor, rect)
        rendered = self.font.render(self.text, self.antialias, self.fgColor)
        # Determine render position
        textRect = rendered.get_rect()
        alignPoints = {left_align: 'topleft',
                       center_align: 'midtop',
                       right_align: 'topright',}
        setattr(textRect, alignPoints[self.align],
                getattr(self.bounds(), alignPoints[self.align]))
        # Render shadow
        if self.shadow:
            renderedShadow = self.font.render(self.text,
                                              self.antialias,
                                              self.shadowColor)
            shadowRect = textRect.move(0, 2)
        else:
            renderedShadow = None
            shadowRect = None
        # Blit text to screen, if necessary
        if renderedShadow is not None and shadowRect.colliderect(rect):
            surface.blit(renderedShadow, shadowRect)
        if textRect.colliderect(rect):
            surface.blit(rendered, textRect)
    
    def optimalSize(self):
        return self.font.size(self.text)
    
    def _getText(self):
        return self._text
    
    def _setText(self, text):
        self._text = text
        self.refresh()
    
    def _getFont(self):
        return self._font
    
    def _setFont(self, font):
        self._font = font
        self.refresh()
    
    def _getAlign(self):
        return self._align
    
    def _setAlign(self, align):
        if align in (left_align, center_align, right_align):
            self._align = align
        else:
            raise ValueError("Alignment %r is not valid" % align)
    
    text = property(_getText, _setText)
    font = property(_getFont, _setFont)
    align = property(_getAlign, _setAlign)

class ImageWidget(Widget):
    def __init__(self, image, stretch=False, *args, **kw):
        super(ImageWidget, self).__init__(*args, **kw)
        self.image = image
        self.stretch = stretch
    
    def draw(self, surface, rect):
        super(ImageWidget, self).draw(surface, rect)
        image = self.image
        if self.stretch and self.rect.size != image.get_size():
            image = pygame.transform.scale(self.image, rect.size)
        surface.blit(image, (0, 0), rect)
    
    def getImage(self):
        """
        Retrieves the current image.
        
        You can also use the ``image`` property.
        """
        return self.__image
    
    def setImage(self, image, tryIM=True):
        """
        Changes the current image.
        
        You can also use the ``image`` property, but it always tries
        `sprites.ImageManager`.
        """
        self.__image = sprites.getImage(image, tryIM)
        self.refresh()
    
    def optimalSize(self):
        return self.image.get_size()
    
    image = property(getImage, setImage)

class CursorWidget(ImageWidget):
    def __init__(self, hotspot=(0, 0), *args, **kw):
        super(CursorWidget, self).__init__(*args, **kw)
        self.hotspot = hotspot
        self.followMouse()
    
    def handle(self, event):
        if event.type == MOUSEMOTION:
            self.followMouse(event.pos)
            return True
        else:
            return False
    
    def followMouse(self, pos=None):
        """Called to follow the mouse."""
        if pos is None:
            pos = pygame.mouse.get_pos()
        self.rect.topleft = self.stlpoint((pos[0] - self.hotspot[0],
                                           pos[1] - self.hotspot[1]))

class ButtonState(object):
    """A button state."""
    def setState(self, button):
        """Called to change the button into the given state."""
        pass
    
    def unsetState(self, button):
        """Called to undo the effects of `setState`."""
        pass
    
    def optimalSize(self):
        """Returns the optimal size of the button, or ``None``."""
        return None

class StretchState(ButtonState):
    """
    A button state in which three images are used.
    
    Two are used for caps, and the center is stretched to fit the text.
    """
    def __init__(self, text, textColor, imgL, imgC, imgR):
        self.text = text
        self.textColor = textColor
        self.imgL = sprites.getImage(imgL)
        self.imgC = sprites.getImage(imgC)
        self.imgR = sprites.getImage(imgR)
    
    def setState(self, button):
        # Calculate left cap rect
        lrect = Rect(0, 0, 0, 0)
        lrect.size = self.imgL.get_size()
        lrect.topleft = (0, 0)
        # Calculate right cap rect
        rrect = Rect(0, 0, 0, 0)
        rrect.size = self.imgR.get_size()
        rrect.topright = (button.rect.width, 0)
        # Calculate center cap rect
        crect = Rect(0, 0, 0, 0)
        crect.height = self.imgC.get_height()
        crect.width = rrect.left - lrect.right
        crect.topleft = lrect.topright
        # Add children
        ImageWidget(self.imgL,
                    parent=button,
                    rect=lrect)
        ImageWidget(self.imgC,
                    stretch=True,
                    parent=button,
                    rect=crect)
        ImageWidget(self.imgR,
                    parent=button,
                    rect=rrect)
        TextWidget(self.text,
                   font=self.getFont(),
                   align=center_align,
                   fgColor=self.textColor,
                   parent=button,
                   rect=crect)
    
    def unsetState(self, button):
        button.removeAllChildren()
        
    def getFont(self):
        return pygame.font.Font(None, self.imgC.get_height())
    
    def optimalSize(self):
        font = self.getFont()
        width = (self.imgL.get_width() +
                 font.size(self.text)[0] +
                 self.imgR.get_width())
        height = self.imgC.get_height()
        return (width, height)

class Button(Widget):
    """Abstract superclass for buttons."""
    def __init__(self,
                 state,
                 callback=None,
                 args=[],
                 kw={},
                 *initArgs, **initKw):
        self.nav_up = initKw.pop('up', None)
        self.nav_down = initKw.pop('down', None)
        self.nav_left = initKw.pop('left', None)
        self.nav_right = initKw.pop('right', None)
        super(Button, self).__init__(*initArgs, **initKw)
        self.setState(state)
        self.callback = callback
        self.callArgs = args
        self.callKw = kw
    
    def handle(self, event):
        keyButtons = {K_UP: self.nav_up,
                      K_DOWN: self.nav_down,
                      K_LEFT: self.nav_left,
                      K_RIGHT: self.nav_right,}
        hatButtons = {(0, 1): self.nav_up,
                      (0, -1): self.nav_down,
                      (-1, 0): self.nav_left,
                      (1, 0): self.nav_right,}
        if event.type == KEYUP and keyButtons.get(event.key) is not None:
            keyButtons[event.key].focus()
            return True
        elif event.type == JOYHATMOTION and \
             hatButtons.get(event.value) is not None:
            hatButtons[event.value].focus()
            return True
        else:
            return False
    
    def setState(self, newState):
        try:
            oldState = self.state
        except AttributeError:
            pass
        else:
            if oldState == newState:
                return
            oldState.unsetState(self)
        self.state = newState
        self.state.setState(self)
    
    def perform(self):
        """Calls the button's callback."""
        if self.callback is not None:
            self.callback(self, *self.callArgs, **self.callKw)
    
    def optimalSize(self):
        """Sizes the button to the optimum size."""
        return self.state.optimalSize()
    
    def rectChanged(self, oldRect, newRect):
        self.state.unsetState(self)
        self.state.setState(self)
    
    def __getattribute__(self, name):
        value = super(Button, self).__getattribute__(name)
        if name.startswith('nav_') and value is not None:
            value = value()
            if value is None:
                setattr(self, name, None)
        return value
    
    def __setattr__(self, name, value):
        if name.startswith('nav_') and value is not None:
            value = weakref.ref(value)
        super(Button, self).__setattr__(name, value)

class PushButton(Button):
    def __init__(self,
                 normState,
                 rollState=None,
                 *args, **kw):
        super(PushButton, self).__init__(normState, *args, **kw)
        self.normState = normState
        if rollState is None:
            self.rollState = self.normState
        else:
            self.rollState = rollState
        self._lastMousePos = pygame.mouse.get_pos()
    
    def handle(self, event):
        if super(PushButton, self).handle(event):
            return True
        elif (event.type == MOUSEBUTTONUP and event.button == 1) or \
             (event.type == KEYUP and event.key == K_RETURN) or \
             (event.type == JOYBUTTONUP and event.button == 0):
            self.perform()
            return True
        else:
            return False
    
    def update(self):
        mousePos = pygame.mouse.get_pos()
        if mousePos != self._lastMousePos:
            self._lastMousePos = mousePos
            mouseInButton = self.screenRect().collidepoint(mousePos)
            if not self.isActive() and mouseInButton:
                self.focus()
            elif self.isActive() and not mouseInButton:
                self.blur()
    
    def canFocus(self):
        return True
    
    def focus(self, *args, **kw):
        success = super(PushButton, self).focus(*args, **kw)
        if success:
            self.setState(self.rollState)
        return success
    
    def blur(self, *args, **kw):
        success = super(PushButton, self).blur(*args, **kw)
        if success:
            self.setState(self.normState)
        return success
