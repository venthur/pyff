# Textbox.py
# Copyright (C) 2009  Matthias Treder
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

""" 
Implements a Textbox which you can use to present information on the screen
during the experiment. It includes automatic linebreak. To enforce linebreaks,
include the sequence '\n' in your text string.

Textbox objects have a number of visual features:
* text - the text itself (eg "A") 
* color - the color of the text (eg (255,255,255) for white)
* textsize - the size of the text
* size - the size of the textbox (width,height)
* edgecolor - if set, the box has an edge of the given color
* antialias
* colorkey - transparent color (default 0,0,0) 

The textbox is not intended for use as a flashing target, so specifying states
does not have any effect. You can change the object, though, by changing
its features manually and calling refresh. 
  
"""
    
import pygame

from VisualElement import VisualElement


class Textbox(VisualElement):

    
    DEFAULT_TEXT = "#"
    DEFAULT_COLOR = 255, 255, 255
    DEFAULT_TEXTSIZE = 20
    DEFAULT_SIZE = (100, 100)
    DEFAULT_EDGECOLOR = None
    DEFAULT_ANTIALIAS = True
    DEFAULT_COLORKEY = 0, 0, 0
    
    def __init__(self, pos=(0, 0), text=DEFAULT_TEXT, color=DEFAULT_COLOR, textsize=DEFAULT_TEXTSIZE, size=DEFAULT_SIZE, edgecolor=DEFAULT_EDGECOLOR, antialias=DEFAULT_ANTIALIAS, colorkey=DEFAULT_COLORKEY):
        VisualElement.__init__(self, 1, pos)
        self.text = text
        self.color = color
        self.textsize = textsize
        self.size = size    
        self.edgecolor = edgecolor
        self.antialias = antialias
        self.colorkey = colorkey
        self.marge = 4          # marge between text and the box boundaries

    def refresh(self):
        font = pygame.font.Font(None, self.textsize)
        boxw, boxh = self.size
        lines = []
        # To process enforced linebreaks, split according to '\n's
        chunks = self.text.split("\n")
        for chunk in chunks:
            text = chunk.split(" ")     # Get a list of single words
            word = None
            currenth = self.marge
            while  currenth < boxh and len(text) > 0:
                linetext = text.pop(0)          # Get first word
                w, h = font.size(linetext)
                if w >= boxw - 2 * self.marge or len(text) == 0:
                    oldtext = linetext
                else:
                    while w < boxw - self.marge and len(text) > 0:
                        oldtext = linetext
                        word = text.pop(0)
                        linetext += " " + word # Attach next word
                        w, h = font.size(linetext)
                        
                    # Check if one word too much was popped, then put it back
                    if w >= boxw - self.marge: text.insert(0, word)
                    else:       # Finished
                        oldtext = linetext 
                lines.append(font.render(oldtext, self.antialias, self.color))
                currenth += h

        # Blit them together
        self.image = pygame.Surface(self.size)
        self.image.fill(self.colorkey)
        if self.edgecolor is not None:
            pygame.draw.rect(self.image, self.edgecolor, (0, 0, boxw, boxh), 1)
        self.image.set_colorkey(self.colorkey)
        x, y = self.marge, self.marge 
        for i in range(len(lines)):
            self.image.blit(lines[i], (x, y + i * h))
        self.image = self.image.convert()
        self.rect = self.image.get_rect(center=self.pos)
        self.images[0] = self.image
        self.rects[0] = self.rect
        
