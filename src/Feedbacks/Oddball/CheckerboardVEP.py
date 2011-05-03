#!/usr/bin/env python


# Copyright (C) 2009  Simon Scholler
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

from Feedbacks.Oddball.Visual import VisualOddball


class CheckerboardVEP(VisualOddball.VisualOddball):
    
    def init(self):
        super(CheckerboardVEP,self).init()
        self.dev_perc = 0.5
        self.nStim = 40
        self.nStim_per_block = 20   # number of stimuli until a pause
        self.dd_dist = 1
        self.squaresPerSide = 6
        self.squaresize = 20
        self.fixdotsize = 10
        self.response = 'none'
        self.give_feedback = False
        self.feedback_duration, self.responsetime_duration = 0,0
        self.stim_duration = 1500      
        self.beforestim_ival = [0,0]
        self.backgroundColor = (50,50,50)
        self.offset = (50,-50)

    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file.
        """
        raise Exception('Not implemented yet')


    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.
        """
        #size = (self.screen_pos[-1]*2/3,self.screen_pos[-1]*2/3)
        size = (self.squaresPerSide*self.squaresize,self.squaresPerSide*self.squaresize)
        cb1 = pygame.Surface(size)
        cb2 = pygame.Surface(size)
        white = (255,255,255)
        black = (1,1,1)
        red = (200,0,0)
        colors = [white,black]
        #squaresize = size[1]*1.0/self.squaresPerSide
        sign = 1
        for y in range(self.squaresPerSide):
            for x in range(self.squaresPerSide):
                rect = (x*self.squaresize,y*self.squaresize,self.squaresize,self.squaresize)
                if not(self.squaresPerSide%2==0 and x==0):
                    sign = -sign
                pygame.draw.rect(cb1, colors[(sign*1+1)/2], rect)
                pygame.draw.rect(cb2, colors[(sign*-1+1)/2], rect)                
        pygame.draw.circle(cb1, red, (size[0]/2, size[0]/2), self.fixdotsize)
        pygame.draw.circle(cb2, red, (size[0]/2, size[0]/2), self.fixdotsize)
        return [cb1], [cb2]

    def start_stimulus(self, stim):
        """
        Draw the stimulus onto the screen.
        """
        middle = self.screen.get_rect().center
        c = (self.offset[0]+middle[0],self.offset[1]+middle[1])
        stimRect = stim.get_rect(center=c)
        self.screen.blit(stim, stimRect)
        pygame.display.update()

    def stop_stimulus(self, stim):
        """
        Remove the stimulus from the screen.
        """
        self.draw_initial()

if __name__ == '__main__':
    cbvep = CheckerboardVEP()
    cbvep.on_init()
    cbvep.on_play()

