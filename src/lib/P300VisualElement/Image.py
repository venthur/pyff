# Image.py
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
Loads one or more images from a file as for use in the P300 speller. 
P300 Image objects have a number of visual features:
* file - give path to the file
* fliplr - flip image horizontally 
* flipud - flip image vertically
* scale - provide a tupel (new_width,new_height) for smoothscaling the element 

Please always provide your path using forward slahes.

The features can be used to specify different states. If some of
these features are constant (eg, the file is used in all
states), you should provide a common value for this feature when you 
instantiate a P300Text.

"""

import os.path

import pygame

from VisualElement import VisualElement


class Image(VisualElement):

    DEFAULT_FILE = None
    DEFAULT_FLIPLR = False
    DEFAULT_FLIPUD = False
    DEFAULT_SCALE = None

    
    def __init__(self, nr_states=2, pos=(0, 0), file=DEFAULT_FILE, fliplr=DEFAULT_FLIPLR, flipud=DEFAULT_FLIPUD, scale=DEFAULT_SCALE):
        VisualElement.__init__(self, nr_states, pos)
        self.file = os.path.normpath(file)
        self.fliplr = self.DEFAULT_FLIPLR
        self.flipud = self.DEFAULT_FLIPUD
        self.scale = self.DEFAULT_SCALE
        self.image = self.load_image(self.file)
        self.rect = self.image.get_rect()

    def refresh(self):
        # For each state, generate image and rect
        for i in range(self.nr_states):
            if self.states[i].has_key("file"):    file = self.states[i]["file"]
            else: file = self.file            # Take standard value
            if self.states[i].has_key("fliplr"):    fliplr = self.states[i]["fliplr"]
            else: fliplr = self.fliplr          # Take standard value
            if self.states[i].has_key("flipud"):    flipud = self.states[i]["flipud"]
            else: flipud = self.flipud            # Take standard value
            if self.states[i].has_key("scale"):    scale = self.states[i]["scale"]
            else: scale = self.scale            # Take standard value
            image = self.load_image(file)
            if fliplr or flipud:
                image = pygame.transform.flip(image, fliplr, flipud)
            if scale is not None:
                image = pygame.transform.smoothscale(image, scale)
            image = image.convert()
            self.images[i] = image
            self.rects[i] = self.images[i].get_rect(center=self.pos)
    
    def load_image(self, file):
        image = None
#        try:
        image = pygame.image.load_basic(file)
 #       except pygame.error, message:
  #          print 'Cannot load image:', file
        #image = image.convert()
        return image

