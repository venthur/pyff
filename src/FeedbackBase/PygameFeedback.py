# PygameFeedback.py -
# Copyright (C) 2009  Bastian Venthur
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

"""This module contains the PygameFeedback baseclass."""

import os

import pygame

from MainloopFeedback import MainloopFeedback


class PygameFeedback(MainloopFeedback):
    """Baseclass for Pygame based Feedbacks.
    
    This class is derived from MainloopFeedback and brings some common 
    functinality shared by most Feedbacks using Pygame.

    Upon start it initializes pygame and calls initialize_graphics which can be
    overwritten by derived classes.

    It also takes care of shutting down pygame automatically upon stop, quit or 
    crash of the feedback.

    After initialization of the feedback, it has some object variables which 
    influence the Feedback's behaviour:
    
    * FPS: (frames per second) influencees how much the Feedback advances in \
            time during a tick call.
    * screenPos: List of integers holding the initial position of the pygame \
            window.
    * screenSize: List of intigers holding the initial size of the pygame \
            window.
    * fullscreen: Boolean
    * caption: String holding the initial value of the window caption.
    * elapsed: Fload holding the elapsed second since the last tick
    * backgroundColor: List of three integers holding the initial background \
            colour
    * keypressed: Boolean holding if a key was pressed
    * lastkey: Last key
    """

    def init(self):
        """Set some PygameFeedback variables to default values."""
        self.FPS = 30
        self.screenPos = [0, 0]
        self.screenSize = [800, 600]
        self.fullscreen = False
        self.caption = "PygameFeedback"
        self.elapsed = 0
        self.backgroundColor = [0, 0, 0]
        # For keys
        self.keypressed = False
        self.lastkey = None


    def pre_mainloop(self):
        """Initialize pygame and graphics."""
        self.init_pygame()
        self.init_graphics()


    def post_mainloop(self):
        """Quit pygame."""
        self.quit_pygame()


    def tick(self):
        """Process pygame events and advance time for 1/FPS seconds."""
        self.process_pygame_events()
        self.elapsed = self.clock.tick(self.FPS)


    def pause_tick(self):
        pass


    def play_tick(self):
        pass


    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screenPos[0],
                                                        self.screenPos[1])
        pygame.init()
        pygame.display.set_caption(self.caption)
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screenSize[0],
                                                   self.screenSize[1]),
                                                   pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screenSize[0],
                                                   self.screenSize[1]),
                                                   pygame.RESIZABLE)
        self.clock = pygame.time.Clock()


    def quit_pygame(self):
        pygame.quit()


    def init_graphics(self):
        """
        Called after init_pygame.

        Derived Classes overwrite this method.
        """
        pass


    def process_pygame_events(self):
        """
        Process the the pygame event queue and react on VIDEORESIZE.
        """
        for event in pygame.event.get():
            self.process_pygame_event(event)

            
    def process_pygame_event(self, event):
        """Process a signle pygame event."""
        if event.type == pygame.VIDEORESIZE:
            e = max(event.w, int(round(event.h * 0.9)))
            self.screen = pygame.display.set_mode((e, event.h), pygame.RESIZABLE)
            self.resized = True
            self.screenSize = [self.screen.get_height(), self.screen.get_width()]
            self.init_graphics()
        elif event.type == pygame.QUIT:
            self.on_stop()
        elif event.type == pygame.KEYDOWN:
            self.keypressed = True
            self.lastkey = event.key
            self.lastkey_unicode = event.unicode
                
    
    def wait_for_pygame_event(self):
        """Wait until a pygame event orcurs and process it."""
        event = pygame.event.wait()
        self.process_pygame_event(event)

