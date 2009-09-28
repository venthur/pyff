# EyetrackerFeedback.py
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


import sys, random, os

import pygame

from FeedbackBase.MainloopFeedback import MainloopFeedback
from lib.P300VisualElement.Textbox import Textbox
from lib.P300Aux.P300Functions import wait_for_key, show_message
from lib.eyetracker import EyeTracker


class EyetrackerFeedback(MainloopFeedback):
    
    DEFAULT_SCREEN_WIDTH, DEFAULT_SCREEN_HEIGHT = 1280, 1024
    DEFAULT_FULLSCREEN = True
    DEFAULT_BGCOLOR = 0, 0, 0                 # Default background color

    " Settings for textmessages via the function show_message() "
    DEFAULT_TEXTSIZE = 40
    DEFAULT_TEXTCOLOR = 255, 255, 255
    
    " Settings for pygame "
    DEFAULT_VIDEO_DRIVER = 'directx' 
    
    " *** Overwritten MainloopFeedback methods *** "
    def init(self):
        self.window_title = "Intelligaze Feedback"
        self.screenWidth, self.screenHeight = self.DEFAULT_SCREEN_WIDTH, self.DEFAULT_SCREEN_HEIGHT
        """ Canvas: The part of the screen which is used for painting!
        That's more efficient than repainting the whole of the screen 
        """
        self.canvasWidth, self.canvasHeight = self.screenWidth, self.screenHeight
        self.fullscreen = self.DEFAULT_FULLSCREEN
        self.bgcolor = self.DEFAULT_BGCOLOR
        self.textsize = self.DEFAULT_TEXTSIZE 
        self.textcolor = self.DEFAULT_TEXTCOLOR
        # Random number generator
        self.random = random.Random()           # Get random generator
        
        self.video_driver = self.DEFAULT_VIDEO_DRIVER
        # Timing
        self.fps = 30
        
    def pre_mainloop(self):
        self._init_pygame()
        # Create visual elements 
        star_dist = 20
        textsize, textcolor = 30, (255, 255, 255)
        size2, color2 = 60, (100, 100, 200)
        font = pygame.font.Font(None, textsize)
        self.cross = font.render("+", False, textcolor);
        font = pygame.font.Font(None, size2)
        star = font.render("*", False, color2);
        self.objects_im, self.objects_rect = [], []
        # Add 5 stars and their rectangles
        for i in range(5): self.objects_im.append(star)
        self.objects_rect.append(star.get_rect(center=(star_dist, star_dist)))
        self.objects_rect.append(star.get_rect(center=(star_dist, self.screenHeight - star_dist)))
        self.objects_rect.append(star.get_rect(center=(self.screenWidth - star_dist, star_dist)))
        self.objects_rect.append(star.get_rect(center=(self.screenWidth - star_dist, self.screenHeight - star_dist)))
        self.objects_rect.append(star.get_rect(center=(self.screenWidth / 2, self.screenHeight / 2)))
        self.screen.blit(self.background, self.background_rect)
        pygame.display.flip()
        # Start eye tracker
        self.et = EyeTracker()
        self.et.start()

    def _init_pygame(self):
        # Initialize pygame, open screen and fill screen with background color
        os.environ['SDL_VIDEODRIVER'] = self.video_driver   # Set video driver
        pygame.init()
        self.clock = pygame.time.Clock()
        if self.fullscreen:
            opts = pygame.FULLSCREEN | pygame.DOUBLEBUF#|pygame.HWSURFACE
            self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), opts)
        else:
            self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight))
        self.background = pygame.Surface((self.canvasWidth, self.canvasHeight)) 
        self.background.fill(self.bgcolor)
        self.background_rect = self.background.get_rect(center=(self.screenWidth / 2, self.screenHeight / 2))
        self.screen.blit(self.background, self.background_rect)
        pygame.display.flip()
        self.font = pygame.font.Font(None, self.textsize)
            
    def post_mainloop(self):
        # Un-initialize all references to pygame objects before shutting down pygame
        self.background = None
        self.background_rect = None
        self.cross = None
        self.objects_im = None
        self.objects_rect = None
        self.screen = None
        self.clock = None
        self.font = None
        pygame.mixer.quit() 
        pygame.quit()
        # Stop eyetracker
        self.et.stop()

    def tick(self):
        # Check event cue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_stop() 
            
    def pause_tick(self):
        self.screen.blit(self.background, self.background_rect)
        pygame.display.flip()
        pygame.time.delay(100)
        
    def play_tick(self):
        self.screen.blit(self.background, self.background_rect)
        # Cross
        x, y, dur = self.et.x, self.et.y, self.et.duration
        if x is not None:
            rect = self.cross.get_rect(center=(x, y)) 
            self.screen.blit(self.cross, rect)
        # Stars
        for i in range(5):
            self.screen.blit(self.objects_im[i], self.objects_rect[i])
        # Display info
        
        txt = self.font.render(str(x) + " / " + str(y) + " / " + str(dur), True, self.textcolor)
        txt_rect = txt.get_rect(center=(100, 50))
        self.screen.blit(txt, txt_rect)      
        pygame.display.flip()
        self.clock.tick(self.fps)

if __name__ == "__main__":
    a = EyetrackerFeedback()
    a.on_init()
    a.on_play()
