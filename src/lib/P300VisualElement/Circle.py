# Circle.py
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
Implements a circle. 
Circle objects have the following features:
* text 
    text on the circle (circle is without text if no text provided)
* textcolor 
    RGB color of the text. If circular layout is used (see below)
    and the flag bunter_kreis is set, you can also provide a tuple 
    of RGB values so that each letter gets its own color   
* textsize 
    size of the text   
* color 
    fill color 
* radius 
    radius of the circle in px
* antialias 
    set whether circle and text should be antialiased
* circular_layout 
    if true, the letters comprising the text will be placed in regular distances at the edge of the circle
* circular_offset 
    if circular layout is used, give the angular position (in radians) of the first element
 * bunter_kreis
    if true and circular layout is used, each letter is assigned a unique color provided in textcolor
"""
import math
import pygame
from VisualElement import VisualElement

class Circle(VisualElement):

    
    DEFAULT_TEXT = None
    DEFAULT_TEXTCOLOR = 200, 200, 200
    DEFAULT_TEXTSIZE = 20
    DEFAULT_COLOR = 255, 255, 0
    DEFAULT_RADIUS = 30
    DEFAULT_ANTIALIAS = True
    DEFAULT_COLORKEY = None
    """ If true, text will be split into single letters that are placed equi-spaced 
    on the circles """
    DEFAULT_CIRCULAR_LAYOUT = False   
    DEFAULT_CIRCULAR_OFFSET = 0
    DEFAULT_BUNTER_KREIS = False
        
    def __init__(self, nr_states=2, pos=(0, 0), text=DEFAULT_TEXT, textcolor=DEFAULT_TEXTCOLOR, textsize=DEFAULT_TEXTSIZE, color=DEFAULT_COLOR, radius=DEFAULT_RADIUS, antialias=DEFAULT_ANTIALIAS, colorkey=DEFAULT_COLORKEY, circular_layout=DEFAULT_CIRCULAR_LAYOUT, circular_offset=DEFAULT_CIRCULAR_OFFSET, bunter_kreis=DEFAULT_BUNTER_KREIS):
        VisualElement.__init__(self, nr_states, pos)
        self.text = text
        self.textcolor = textcolor
        self.textsize = textsize
        self.color = color
        self.radius = radius
        #self.edgewidth = edgewidth
        #self.edgecolor = edgecolor
        self.antialias = antialias
        self.colorkey = colorkey
        self.circular_layout = circular_layout
        self.circular_offset = circular_offset
        self.bunter_kreis = bunter_kreis 
        if circular_layout:
            self.textimages = [None] * len(text)
            self.textrects = [None] * len(text)
        self.letter_pos = []            # Letter positions relative to surface are also saved

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
            #if self.states[i].has_key("edgecolor"):    edgecolor = self.states[i]["edgecolor"]
            #else: edgecolor = self.edgecolor          # Take standard value
            if self.states[i].has_key("radius"):    radius = self.states[i]["radius"]
            else: radius = self.radius         # Take standard value
            if self.states[i].has_key("circular_layout"): circular_layout = self.states[i]["circular_layout"]
            else: circular_layout = self.circular_layout # Take standard value
            if self.states[i].has_key("circular_offset"): circular_offset = self.states[i]["circular_offset"]
            else: circular_offset = self.circular_offset # Take standard value
            
            # Create the text elements "
            font = pygame.font.Font(None, textsize)
            if not circular_layout:  # Just normal text
                textimage = font.render(text, self.antialias, textcolor);
                textrect = textimage.get_rect()
                w2, h2 = textrect.width / 2, textrect.height / 2
            else:
                # Calculate the letter positions
                nrLetters = len(text)
                angDistance = 2 * math.pi / nrLetters     # Angular distance between letters
                for j in range(nrLetters):
                    # Check if multiple colors are available
                    if self.bunter_kreis: color_now = textcolor[j]
                    else: color_now = textcolor
                    theta = angDistance * j + circular_offset
                    x = (radius - textsize / 2) * math.cos(theta) + radius
                    y = (radius - textsize / 2) * math.sin(theta) + radius
                    self.textimages[j] = font.render(text[j], self.antialias, color_now)
                    self.textrects[j] = self.textimages[j].get_rect(center=(x, y))
                    # Save the letter positions for state=0
                    if i == 0: self.letter_pos.append((x, y))

            # Create surface & draw the circle area
            #marge = 4       # Add a marge to ensure that the whole object is drawn
            #cx = cy = radius+0.5 + marge/2      # Center coordinates of object
            if self.antialias:
                # Start with a 2x bigger circle and size down to achieve antialias
                image = pygame.Surface((4 * radius, 4 * radius))
                if self.colorkey: image.fill(self.colorkey)
                pygame.draw.circle(image, color, (2 * radius, 2 * radius), 2 * radius)
                image = pygame.transform.smoothscale(image, (2 * radius, 2 * radius))
            else:
                image = pygame.Surface((2 * radius, 2 * radius))
                if self.colorkey: image.fill(self.colorkey)
                pygame.draw.circle(image, color, (radius, radius), radius)
         
            """
            " Draw the edge "
            num_samples = 10*radius         # The bigger the circle, the more samples you'll need
            xy = []
            polar_stepsize = 2*math.pi/num_samples 
            " Sample points on the circle to connect them with straight lines "
            for j in range(num_samples):
                phi = polar_stepsize*j
                x,y = int(cx+radius*math.cos(phi)) , int(cy+radius*math.sin(phi))
                xy.append( (x,y) )
            if self.antialias:
                if edgecolor is None: edgecolor = color
                pygame.draw.aalines(image,edgecolor,True,xy,0)
            elif edgecolor is not None:
                pygame.draw.lines(image,edgecolor,True,xy)
            """
               
            # Put text and circle together
            if not circular_layout:
                image.blit(textimage, (radius - w2, radius - h2))
            else: 
                for j in range(len(self.textimages)):
                    image.blit(self.textimages[j], self.textrects[j])

            if self.colorkey is not None: image.set_colorkey(self.colorkey)
            
            image = image.convert()
            self.images[i] = image 
            self.rects[i] = self.images[i].get_rect(center=self.pos)
