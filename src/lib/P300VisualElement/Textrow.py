# Textrow.py
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
Simpler version of Textbox. Implements only a single row and does not 
support linebreaks. Other than in Textbox, you can have letters
being highlighted (by a different color)   

Textbox objects have a number of visual features:
* text - the text itself (eg "A") 
* color - the color of the text (eg (255,255,255) for white)
* textsize - the size of the text
* size - the size of the textbox (width,height)
* edgecolor - if set, the box has an edge of the given color
* antialias
* colorkey - transparent color (default 0,0,0) 
* highlight - the index/indices of the letter(s) you want to highlight
* highlight_color - the color of the highlighted elements 
* highlight_size - the size of the highlighted elements

Textrow is not intended for use as a flashing target, so specifying states
does not have any effect. You can change the object, though, by changing
its features manually and calling refresh. 
  
  
"""

    
import pygame

from VisualElement import VisualElement


class Textrow(VisualElement):

    
    DEFAULT_TEXT = "#"
    DEFAULT_COLOR = 255, 255, 255
    DEFAULT_TEXTSIZE = 20
    DEFAULT_SIZE = (100, 100)
    DEFAULT_EDGECOLOR = None
    DEFAULT_ANTIALIAS = True
    DEFAULT_COLORKEY = 0, 0, 0
    DEFAULT_HIGHLIGHT = None
    DEFAULT_HIGHLIGHT_COLOR = None
    
    def __init__(self, pos=(0, 0), text=DEFAULT_TEXT, color=DEFAULT_COLOR, textsize=DEFAULT_TEXTSIZE, size=DEFAULT_SIZE, edgecolor=DEFAULT_EDGECOLOR, highlight=DEFAULT_HIGHLIGHT, highlight_color=DEFAULT_HIGHLIGHT_COLOR, highlight_size=DEFAULT_TEXTSIZE, antialias=DEFAULT_ANTIALIAS, colorkey=DEFAULT_COLORKEY):
        VisualElement.__init__(self, 1, pos)
        self.text = text
        self.color = color
        self.textsize = textsize
        self.size = size    
        self.edgecolor = edgecolor
        self.antialias = antialias
        self.colorkey = colorkey
        self.highlight = highlight
        self.highlight_color = highlight_color 
        self.highlight_size = highlight_size 
        self.leftmarge = 4          # marge between text and the left box boundaries

    def refresh(self):
        font = pygame.font.Font(None, self.textsize)
        hi_font = pygame.font.Font(None, self.highlight_size) 
        boxw, boxh = self.size
        chunks = []
        if self.highlight is not None:
            # Run through the text and create letter for letter
            for pos in range(len(self.text)):
                letter = self.text[pos]
                if pos in self.highlight:
                    chunks.append(hi_font.render(letter, self.antialias, self.highlight_color))
                else:
                    chunks.append(font.render(letter, self.antialias, self.color))
        else:
            chunks.append(font.render(self.text, self.antialias, self.color)) # render whole text
            
        # Prepare surface & draw border
        self.image = pygame.Surface(self.size)
        self.image.fill(self.colorkey)
        if self.edgecolor is not None:
            pygame.draw.rect(self.image, self.edgecolor, (0, 0, boxw, boxh), 1)
        self.image.set_colorkey(self.colorkey)
        
        # Put text
        xpos = self.leftmarge
        for s in chunks:
            w = s.get_width()
            r = s.get_rect(center=(xpos + w / 2, self.size[1] / 2 + 2))  # +2 for vertical alignment
            self.image.blit(s, r)
            xpos += w

        self.image = self.image.convert()
        self.rect = self.image.get_rect(center=self.pos)
        self.images[0] = self.image
        self.rects[0] = self.rect
        
