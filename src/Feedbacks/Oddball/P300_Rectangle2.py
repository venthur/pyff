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

"""
An oddball paradigm. The count is entered via the keyboard at the end
of the sequence and its sent as a trigger (incremented by 100).
"""
import pygame
import math
import sys

from Feedbacks.Oddball.Visual import VisualOddball
from lib.P300VisualElement.Textrow import Textrow


class P300_Rectangle(VisualOddball.VisualOddball):
    
    def init(self):
        super(P300_Rectangle,self).init()
        self.dev_perc = 0.2
        self.nStim = 5
        self.dd_dist = 2
        self.response = 'none'
        self.promptCount = False                # If yes, asks to type in a count in the end
        self.give_feedback = False
        self.feedback_duration, self.beforestim_ival = 0, [0,0]
        self.stim_duration = 1500
        self.responsetime_duration = 0     
        self.backgroundColor = (50,50,50)
        self.within_dev_perc = [0.5,0.5]#[0.5, 0.5]  # sum must be 1
        self.within_std_perc = [1/3,1/3,1/3]  # sum must be 1
        self.userresp = ''
        self.size = (self.screen_pos[-1]*2/3,self.screen_pos[-1]/10) #moved here
        
    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file.
        """
        raise Exception('Not implemented yet')
        
        
    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.          
        """        
        dev1 = pygame.Surface(self.size)
        dev2 = pygame.Surface(self.size)
        std1 = pygame.Surface(self.size)
        std2 = pygame.Surface(self.size)
        std3 = pygame.Surface(self.size)
        red, orange, blue, yellow, grey, green = (255,0,0), (255,100,0), (0,0,255), (255,255,0) , (150,150,150), (0,255,0)
        dev1.fill(red)
        dev2.fill(yellow)
        std1.fill(blue)
        std2.fill(green)
        std3.fill(grey)
        #std4.fill(green)
        #self.STANDARD = [10,11]
        #self.DEVIANT = [30, 31]
        return [std1,std2,std3], [dev1,dev2]

        
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
                if event.unicode == pygame.K_RETURN:
                    #TODO: save user answer
                    pass
                self.userresp = self.userresp + event.unicode                      
    
    
    def pre_mainloop(self):
        VisualOddball.VisualOddball.pre_mainloop(self)
        self.nDev = self.nStim*self.dev_perc
        self.nStd = self.nStim-self.nDev 
        self.devlist = self.create_list(self.nDev, self.within_dev_perc)
        self.stdlist = self.create_list(self.nStd, self.within_std_perc)
                  
    def post_mainloop(self):
        """
        Overwrite superclass function to also
        include a text prompt
        """
        self.send_parallel(self.RUN_END)
        if self.stimuliShown == self.nStim and self.promptCount: # if whole block was finished without interupt->enter count
            self.prompt_count()
        pygame.quit()   

    def prompt_count(self):
        self.countrow = Textrow(text="", pos=self.screen.get_rect().center,textsize=60, color=(150, 150, 255), size=(100, 60), edgecolor=(255, 255, 255), antialias=True, colorkey=(0, 0, 0))
        pygame.event.clear()
        text, ready = "", False
        while not ready:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if k == pygame.K_BACKSPACE:
                        if len(text) > 0: text = text[0: - 1]   # Delete last number
                    elif len(text) < 2:
                        if k in (pygame.K_0,pygame.K_KP0): text = text + "0"
                        elif k in (pygame.K_1,pygame.K_KP1): text = text + "1"
                        elif k in (pygame.K_2,pygame.K_KP2): text = text + "2"
                        elif k in (pygame.K_3,pygame.K_KP3): text = text + "3"
                        elif k in (pygame.K_4,pygame.K_KP4): text = text + "4"
                        elif k in (pygame.K_5,pygame.K_KP5): text = text + "5"
                        elif k in (pygame.K_6,pygame.K_KP6): text = text + "6"
                        elif k in (pygame.K_7,pygame.K_KP7): text = text + "7"
                        elif k in (pygame.K_8,pygame.K_KP8): text = text + "8"
                        elif k in (pygame.K_9,pygame.K_KP9): text = text + "9"
                    elif k == pygame.K_RETURN: ready = True
            self.countrow.text = text
            self.countrow.refresh()
            self.countrow.update(0)
            self.screen.blit(self.background, self.backgroundRect)
            self.screen.blit(self.countrow.image, self.countrow.rect)
            pygame.display.update()
            pygame.time.wait(100)
        # Send count as EEG marker
        self.send_parallel(int(text)+100)


if __name__ == '__main__':
    p300_rect = P300_Rectangle()
    p300_rect.on_init()
    p300_rect.on_play()
            
