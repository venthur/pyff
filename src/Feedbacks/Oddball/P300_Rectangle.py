#!/usr/bin/env python


# Copyright (C) 2008-2009  Simon Scholler
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

"""Checkerboard-flipping used to generate a visual evoked potential (VEP)."""

import pygame
import math
import sys

from Feedbacks.Oddball.Visual import VisualOddball


class P300_Rectangle(VisualOddball.VisualOddball):
    
    def init(self):
        super(P300_Rectangle,self).init()
        self.dev_perc = 0.2
        self.nStim = 40
        self.dd_dist = 2
        self.response = 'none'
        self.give_feedback = False
        self.feedback_duration, self.beforestim_ival = 0, [0,0]
        self.stim_duration = 1500
        self.responsetime_duration = 0     
        self.backgroundColor = (50,50,50)
        self.nDev = self.nStim*self.dev_perc
        self.nStd = self.nStim-self.nDev 
        self.within_dev_perc = [1,0]#[0.5, 0.5]  # sum must be 1
        self.within_std_perc = [0.5, 0.5]  # sum must be 1
        self.devlist = self.create_list(self.nDev, self.within_dev_perc)
        self.stdlist = self.create_list(self.nStd, self.within_std_perc)
        self.userresp = ''
        
    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file.
        """
        raise Exception('Not implemented yet')
        
        
    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.          
        """        
        size = (self.screen_pos[-1]*2/3,self.screen_pos[-1]/10)
        dev1 = pygame.Surface(size)
        dev2 = pygame.Surface(size)
        std1 = pygame.Surface(size)
        std2 = pygame.Surface(size)
        red, orange, blue, yellow = (255,0,0), (255,100,0), (0,0,255), (255,255,0) 
        dev1.fill(red)
        dev2.fill(orange)
        std1.fill(blue)
        std2.fill(yellow)
        #self.STANDARD = [10,11]
        #self.DEVIANT = [30, 31]
        return [std1,std2], [dev1,dev2]

        
    def start_stimulus(self, stim):
        """
        Draw the stimulus onto the screen.
        """           
        stimRect = stim.get_rect(center=self.screen.get_rect().center)     
        self.screen.blit(stim, stimRect)
        pygame.display.update()

    def stop_stimulus(self, stim):
        """
        Remove the stimulus from the screen.
        """           
        self.draw_initial()
        
    def get_deviant(self):        
        idx = self.devlist.pop()
        return self.devs[idx], idx
                
    def get_standard(self):
        idx = self.stdlist.pop()
        return self.stds[idx], idx                          
                      
    def process_pygame_events(self):
        """
        Process the pygame event queue and react on VIDEORESIZE.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.unicode == K_RETURN:
                    #TODO: save user answer
                    pass
                self.userresp = self.userresp + event.unicode                      
                      
if __name__ == '__main__':
    p300_rect = P300_Rectangle()
    p300_rect.on_init()
    p300_rect.on_play()
            