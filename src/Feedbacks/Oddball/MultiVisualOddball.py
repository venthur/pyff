#!/usr/bin/env python

# Allows for multiple stimuli in each class. All stimuli should be in the
# folder self.basedir. Then provide DIR_STD and DIR_DEV as a list
# of name (including wildcards if necessary), such as DIR_DEV = ['dev1_*.jpg','dev2_*.jpg'].
# One image of the list will be randomly loaded whenever the stimulus is shown.
#
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

"""Class for visual oddball experiments with multiple possible stimuli per class."""

import pygame
import os,random,time
import glob

from Feedbacks.Oddball.Oddball import Oddball

class MultiVisualOddball(Oddball):
    
    def init(self):
        super(MultiVisualOddball,self).init()
        self.dev_perc = 0.2
        #self.within_std_perc = [0.5, 0.5]  # sum must be 1
        self.within_std_perc = [1]
        self.within_dev_perc = [.4,.6]
        #self.within_dev_perc = [.25,.25,.125,.125,.125,.125]
        self.stimuli = 'load'
        self.nStim = 450
        self.nStim_per_block = 150
        self.dd_dist = 3

        # Timing 
        self.stim_duration = 1000
        self.responsetime_duration = 0     
        self.countdown_from = 3
        
        # Response
        self.give_feedback = False
        self.rsp_key_dev = ' '      # ' ' = space bar
        
        # Graphics
        self.screen_pos = (100,100,800,700)
        self.fixColor = (0,0,255)       # Fix dot color
        self.fixPos = (300,300)         # Fix dot pos in image
        self.fixLen = 4                # Fix dot length or radius

        # An example
        #basedir = '/data/sonstiges/matlab/stimuli/symblobs'   # just for convenience
        #self.DIR_STD = [os.path.join(basedir,'standard_green*.jpg'),os.path.join(basedir,'standard_yellow*.jpg')]
        #self.DIR_DEV = [os.path.join(basedir,'sym_green*.jpg'),os.path.join(basedir,'sym_yellow*.jpg'),os.path.join(basedir,'target*.jpg')]
        #basedir = '/data/sonstiges/matlab/stimuli/symblobs2'   # just for convenience
        #self.DIR_STD = [os.path.join(basedir,'standard_green*.jpg'),os.path.join(basedir,'standard_yellow*.jpg')]
        #self.DIR_DEV = [os.path.join(basedir,'sym_green*.jpg'),os.path.join(basedir,'sym_yellow*.jpg')]
        #self.DIR_DEV.append(os.path.join(basedir,'t4_green*.jpg'))
        #self.DIR_DEV.append(os.path.join(basedir,'t4_yellow*.jpg'))
        #self.DIR_DEV.append(os.path.join(basedir,'t7_green*.jpg'))
        #self.DIR_DEV.append(os.path.join(basedir,'t7_yellow*.jpg'))

        basedir = '/data/sonstiges/matlab/stimuli/symblobs4'   # just for convenience
        self.DIR_STD = [os.path.join(basedir,'standard*.jpg')]
        self.DIR_DEV = [os.path.join(basedir,'sym*.jpg')]
        self.DIR_DEV.append(os.path.join(basedir,'target*.jpg'))

        
        # Initialize random number generator with system time
        random.seed()
        
    def load_stimuli(self):
        """
        Gets a list of absolute paths to deviant and standard stimuli files (NOT the 
        files themselves) for self.DIR_DEV and self.DIR_STD
        """
        stds, devs = [], []
        for stimdir in (self.DIR_STD,self.DIR_DEV):
            if not isinstance(stimdir,list):
                stimdir = [stimdir]         # make a dummy list out of it
            for dir in stimdir:
                if os.path.isdir(dir):
                    dir = os.path.join(dir,'*')     # Append wildcard
                if stimdir is self.DIR_STD:
                    stds.append(glob.glob(dir))
                else:
                    devs.append(glob.glob(dir))
        return stds, devs
        
    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file and returns it as a pygame surface.
        """
        surf = pygame.image.load(filename)
        surf = surf.convert()
        pygame.draw.circle(surf, self.fixColor,self.fixPos,self.fixLen+2)
        #pygame.draw.circle(surf, (0,0,0),self.fixPos,self.fixLen) # black boundary
  #      pygame.draw.rect(surf, self.fixColor, (298,280,5,41))
  #      pygame.draw.rect(surf, self.fixColor, (280,298,41,5))
        return surf
        
    def pre_mainloop(self):
        """
        Sets up all the necessary components (e.g. pygame, stimuli, graphics) 
        to run the experiment.
        """
        self.send_parallel(self.RUN_START)
        self.init_pygame()
        self.get_stimuli()
        self.error_checking()
        self.init_graphics()
        self.gameover = False
        
        self.nDev = self.nStim*self.dev_perc
        self.nStd = self.nStim-self.nDev 
        self.devlist = self.create_list(self.nDev, self.within_dev_perc)
        self.stdlist = self.create_list(self.nStd, self.within_std_perc)    
           
    def get_deviant(self):        
        idx = self.devlist.pop()
        randImage = random.randint(0,len(self.devs[idx])-1)
        filename = self.devs[idx][randImage]
        return self.load_stimulus(filename), idx
        
    def get_standard(self):
        idx = self.stdlist.pop()
        if len(self.stds)>1:
            idx = random.randint(0,len(self.stds)-1)
        else:
            idx = 0
        randImage = random.randint(0,len(self.stds[idx])-1)
        filename = self.stds[idx][randImage]
        return self.load_stimulus(filename), idx
    
    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.          
        """        
        raise Exception('Not implemented yet')

    def start_stimulus(self, stim):
        """
        Draw the stimulus onto the screen.
        """           
        stimRect = stim.get_rect(center=self.screen.get_rect().center)     
        #stim.set_colorkey((0,0,0))
        self.screen.blit(stim, stimRect)
        pygame.display.update()

    def stop_stimulus(self, stim):
        """
        Remove the stimulus from the screen.
        """           
        self.draw_initial()

    def draw_initial(self):
        """
        Draw the default screen layout, but (in contrast to Oddball base class)
        do not update the screen yet (otherwise A BLANK frame will be introduced).
        """            
        self.screen.blit(self.background, self.backgroundRect)
        #pygame.display.update()
        
if __name__ == '__main__':
    odd  = MultiVisualOddball()
    odd.on_init()
    odd.on_play()
