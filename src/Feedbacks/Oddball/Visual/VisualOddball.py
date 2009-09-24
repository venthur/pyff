#!/usr/bin/env python


# Methods that have to implemented by a subclass
# - init:                       if some default settings should be changed
# - load_stimulus:              if stimuli are files (e.g. images, audio-files)    
# - get_predefined_stimuli:     if stimuli are created by a python module
# - present_stimulus:           determines how the stimuli are presented
#
#
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

"""Class for Visual Oddball Experiments."""

import pygame

from Feedbacks.Oddball import Oddball


class VisualOddball(Oddball.Oddball):
    
    def init(self):
        super(VisualOddball,self).init()
        self.dev_perc = 0.25
        self.nStim = 21
        self.dd_dist = 3
        
    
    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file.
        """
        raise Exception('Not implemented yet')
        
        
    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.          
        """        
        size = (self.screen_pos[-1]/3,self.screen_pos[-1]/3)
        # create deviant stimulus
        dev1 = pygame.Surface(size)
        dev1.fill((255,0,0))
        # create standard stimulus
        std1 = pygame.Surface(size)
        std1Rect = std1.get_rect(center=(320,240))
        hs = int(size[0]/2)
        pygame.draw.circle(std1, (0,255,0), (hs,hs), hs)
        return [std1], [dev1]

    def start_stimulus(self, stim):
        """
        Draw the stimulus onto the screen.
        """           
        stimRect = stim.get_rect(center=self.screen.get_rect().center)     
        stim.set_colorkey((0,0,0))
        self.screen.blit(stim, stimRect)
        pygame.display.update()

    def stop_stimulus(self, stim):
        """
        Remove the stimulus from the screen.
        """           
        self.draw_initial()
        
if __name__ == '__main__':
    vo = VisualOddball()
    vo.on_init()
    vo.on_play()        