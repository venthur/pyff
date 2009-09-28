# Rectangle.py
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
A rectangle element for use in a P300 speller. 
Rectangle objects have the following features:
* text - text on the rectangle
* textcolor - RGB color of the text   
* textsize - size of the text   
* color - RGB color of the rectangle 
* size - (width,height) of the rectangle 
* rotate - rotates the whole object counterclockwise (in deg)
* antialias - set whether rectangle should be antialiased
* textantialias - set whether text should be antialiased
"""


import pygame

from VisualElement import VisualElement


class Rectangle(VisualElement):

    DEFAULT_TEXT = None
    DEFAULT_TEXTCOLOR = 200, 200, 200
    DEFAULT_TEXTSIZE = 20
    DEFAULT_COLOR = 255, 255, 0
    DEFAULT_SIZE = (20, 80)
    DEFAULT_ROTATE = None
    DEFAULT_ANTIALIAS = False
    DEFAULT_TEXTANTIALIAS = True
    
    def __init__(self, nr_states=2, pos=(0, 0), text=DEFAULT_TEXT, textcolor=DEFAULT_TEXTCOLOR, textsize=DEFAULT_TEXTSIZE, color=DEFAULT_COLOR, size=DEFAULT_SIZE, rotate=DEFAULT_ROTATE, antialias=DEFAULT_ANTIALIAS, textantialias=DEFAULT_TEXTANTIALIAS):
        VisualElement.__init__(self, nr_states, pos)
        self.text = text
        self.textcolor = textcolor
        self.textsize = textsize
        self.color = color
        self.size = size
        self.rotate = rotate
        self.antialias = antialias
        self.textantialias = textantialias

    def refresh(self):
        # For each state, generate image and rect
        for i in range(self.nr_states):
            if self.states[i].has_key("text"):    text = self.states[i]["text"]
            else: text = self.text            # Take standard value
            if self.states[i].has_key("textcolor"):    textcolor = self.states[i]["textcolor"]
            else: textcolor = self.textcolor          # Take standard value
            if self.states[i].has_key("textsize"):    textsize = self.states[i]["textsize"]
            else: textsize = self.textsize            # Take standard value
            if self.states[i].has_key("color"):    color = self.states[i]["color"]
            else: color = self.color          # Take standard value
            if self.states[i].has_key("rotate"):    rotate = self.states[i]["rotate"]
            else: rotate = self.rotate         # Take standard value
            if self.states[i].has_key("size"):    size = self.states[i]["size"]
            else: size = self.size         # Take standard value

            width, height = size
            # Get the text image
            font = pygame.font.Font(None, textsize)
            textimage = font.render(text, self.textantialias, textcolor);
            if self.antialias is not None:
                textimage = pygame.transform.rotate(textimage, rotate)
            textrect = textimage.get_rect()
            w2, h2 = textrect.width / 2, textrect.height / 2
            # Get the rectangle
            if self.antialias:
                """
                Perform antialiasing with a trick: first draw an image twice
                the desired size, then scale it down with a smoothscaling tool 
                """
                bigimage = pygame.Surface(size)
                bigimage.fill((0, 0, 0))
                bigimage.set_colorkey((0, 0, 0))
                pygame.draw.rect(bigimage, color, (0, 0, 2 * width, 2 * height))
                if rotate is not None:
                    bigimage = pygame.transform.rotate(bigimage, rotate)
                image = pygame.transform.smoothscale(bigimage, (width, height))
            else:
                image = pygame.Surface(size)
                image.fill((0, 0, 0))
                image.set_colorkey((0, 0, 0))
                pygame.draw.rect(image, color, (0, 0, width, height))
                if rotate is not None:
                    image = pygame.transform.rotate(image, rotate)
             
            # Getrect & put them together
            rect = image.get_rect()
            image.blit(textimage, (rect.centerx - w2, rect.centery - h2))
            self.images[i] = image 
            self.rects[i] = self.images[i].get_rect(center=self.pos)
