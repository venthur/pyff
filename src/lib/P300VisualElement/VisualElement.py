# VisualElement.py
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
VisualElement.py -
Copyright (c) 2009  Matthias Sebastian Treder

The base class for elements in a P300 speller 
"""

import random

import pygame


class VisualElement(pygame.sprite.Sprite):
    
    DEFAULT_PICK_RANDOM_STATE = False
    
    def __init__(self, nr_states=2, pos=(0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.state = 0                # Holds the current state of the element as a number (0,1,...)
        self.nr_states = nr_states    # Total number of states the element can have (default 2)
        self.pick_random_state = self.DEFAULT_PICK_RANDOM_STATE # If true, a random new state will be picked upon each call of update
        self.states = []              # A list of dictionaries specifying the states
        self.pos = pos                # Position of the element's center in pixel coordinates
        """ The images and rectangles corresponding to the different states """
        self.images = [None] * nr_states
        self.rects = [None] * nr_states
        self.states = []
        " Each state is specified by a dictionary of (feature,value) combinations"
        for i in range(nr_states): self.states.append(dict())

    def update(self, new_state=None):
        """ 
        This is a sprite method automatically called when the sprite is to be 
        updated. Each call makes the element progress to another state. When 
        the last state had been reached, the element is set back to its original 
        state via the modulus operator.
        Usually, you do not have to override this method.
        If you provide a value >= 0 for new_state, this will be the new state
        of the element. If you provide the value -1 for new_state, the number 
        of the state will be decreased by 1. 
        If pick_random_state is True and no new state is specified, a random
        new state will be picked.
        """
        
        if self.pick_random_state and new_state is None:    # Pick a random state
            old_state = self.state
            rnd = random.Random()
            # Pick 2 random states: if first one is equal to current state, pick second one
            s = range(self.nr_states)
            state2 = rnd.sample(s, 2)
            new_state = (state2[1] if state2[0] == self.state else state2[0])
        else:
            if new_state is None: 
                new_state = self.state + 1
            elif new_state == - 1:
                new_state = self.state - 1
        self.state = new_state % self.nr_states
        self.image = self.images[self.state]
        self.rect = self.rects[self.state]
    
    def refresh(self):
        """ 
        This method should be called after new states have been defined.
        In this method, the images corresponding to the states (self.images())
        and the new rects (self.rects) should be produced. Have a look at the
        subclasses of VisualElement for some examples.  
        """ 
        pass
   
    def set_states(self, nr, features):
        """ 
        Sets the features belonging each state. Upon each call, provide the number
        of the state you want to change and a dictionary of features you want to
        change. The dictionary contains key/value pairs specifying the name of the
        feature you want to change and the corresponding value. Details on which
        features are allowed for each subclass are given in the description of the 
        subclass. 
        """
        for key, value in features.iteritems():
            self.states[nr][key] = value
