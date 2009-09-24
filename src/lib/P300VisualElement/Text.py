# Text.py
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
Implements a Text/Letter Element for use in the visual P300 paradigm.
P300 Text objects have a number of visual features:
* text - the text itself (eg "A") 
* color - the color of the text (eg (255,255,255) for white)
* size - the size of the text (eg 30)

These features can be used to specify different states. If some of
these features are constant (eg, the same letter size is used in all
states), you should provide a common value for this feature when you 
instantiate a P300Text.

Example:
t = P300Text(text="A",size=30) 
"""

    
import pygame

from VisualElement import VisualElement


class Text(VisualElement):

    
    DEFAULT_TEXT = "#"
    DEFAULT_COLOR = 255, 255, 255
    DEFAULT_SIZE = 30

    
    def __init__(self, nr_states=2, pos=(0, 0), text=DEFAULT_TEXT, color=DEFAULT_COLOR, size=DEFAULT_SIZE):
        VisualElement.__init__(self, nr_states, pos)
        self.text = text
        self.color = color
        self.size = size    

    def refresh(self):
        # For each state, generate image and rect
        for i in range(self.nr_states):
            if self.states[i].has_key("text"):    text = self.states[i]["text"]
            else: text = self.text            # Take standard value
            if self.states[i].has_key("color"):    color = self.states[i]["color"]
            else: color = self.color          # Take standard value
            if self.states[i].has_key("size"):    size = self.states[i]["size"]
            else: size = self.size            # Take standard value
            font = pygame.font.Font(None, size)
            self.images[i] = font.render(text, True, color);
            self.rects[i] = self.images[i].get_rect(center=self.pos)