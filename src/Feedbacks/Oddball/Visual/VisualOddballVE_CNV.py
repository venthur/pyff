
# Copyright (C) 2011  Simon Scholler
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

"""Class for Visual Oddball Experiments using Vision Egg for Stimulus Presentation."""

import pygame
#import random
import os
import sys

from scipy import *
import time
import VisionEgg
import random

from VisionEgg.Textures import Texture

from Feedbacks.Oddball.Visual import VisualOddballVE
    
from lib import marker
    
# TODO: 
# - EVTL: hit-miss-counter

# Q:
# - color word  (as in self._view.center_word)  
# - problems with yield (class variables do not get updated!)
# - standard and deviant marker codes: evtl. include in marker.py (ask benjamin, basti)
    
    
class VisualOddballVE_CNV(VisualOddballVE.VisualOddballVE):    
    
    #RUN_START, RUN_END = 252,253
    #COUNTDOWN_START, COUNTDOWN_END = 40,41
    S1, S2 = 10, 11
    IVAL_S1_S2, IVAL_S2_S1 = 20, 21 
    # standards have markers 10,11,12,... ; deviants 30,31,32,... (cf. get_stimuli())
    # if self.group_stim_markers==True, then there exist only two markers, one for
    # group standard (10), and one for group deviant (20)
    #RESP_STD, RESP_DEV = 1,2
    #SHORTPAUSE_START, SHORTPAUSE_END = 249, 250
    
    
    def init_parameters(self):
        
        #self.geometry = [100, 100, 1024, 768]
        self.font_size = 120
        self.font_color_name = "white" #(200, 80, 118) #(145, 54, 146)
        self.bg_color = (198, 210, 221)
        self.center = [self.geometry[2]/2, self.geometry[3]/2]        
        self.nTrials = 20
        self.nTrials_per_block = 6   # has to be an even number
        self.countdown_start = 3
        self.show_standards = True
        self.give_feedback = True
        self.group_stim_markers = False            
        
        self.DIR_DEV = 'C:\img_oddball\dev'
        self.DIR_STD= 'C:\img_oddball\std'
        self.logfilename = 'C:\img_oddball\log.txt'
        
#        stimuli_opts = ['load', 'predefined']
#        self.stimuli = stimuli_opts[1]        
        
        # Response opts
        self.eob_response = True    # response after each block?
        self.response = 'none'      # response after each stimulus presentation?
    
        # Durations of the different blocks        
        self.s1_duration = [1., 10]
        self.s2_duration = 1.
        self.isi_s1_s2 = 1.
        self.isi_s2_s1 = 1.
        
        #self.gameover_duration = 3000
        #self.shortpauseDuration = 10000        
        
        self.std, self.dev = self.load_stimuli()   

        self.responded = True        
        self.bg_color = 'grey'        
        self.error_check()        
        
        
    def run(self):
        
        nBlocks = int(ceil(1.0*self.nTrials/self.nTrials_per_block))
        self.create_log()
                 
        for n in range(nBlocks):
            
            self.user_input = ''
            if n == nBlocks-1 and self.nTrials%self.nTrials_per_block!=0:
                self.create_stim_seq(self.nTrials%self.nTrials_per_block)
            else:
                self.create_stim_seq()
                
            # Init image and text object            
            self.image = self.add_image_stimulus(position=tuple(self.center),on=False)            
            self.text = self.add_text_stimulus(position=tuple(self.center),font_size=self.font_size,on=False) 
    
            # This feedback uses a generator function for controlling the stimulus
            # transition. Note that the function has to be called before passing
            generator = self.prepare()
            
            self._view.countdown()
            
            # Pass the transition function and the pre-stimulus display durations
            # to the stimulus sequence factory. 
            s = self.stimulus_sequence(generator, [self.s1_duration, self.isi_s1_s2, self.s2_duration, self.isi_s2_s1])  
        
            # Start the stimulus sequence
            s.run()            
            self.image.set(on=False)
            
            # User Input
            self.eob_responded = False
            self.text.set(text='Type in #Deviants',on=True)
            while not self.eob_responded:
                self._view.update()           
            self.text.set(text='',on=False)
            self.write_log(self.user_input+'\n')
            
            # Break or End of Session
            if n == nBlocks-1:
                self._view.present_center_word('End of Session', 10)
            else:
                self._trigger(marker.PAUSE_START, wait=True)
                self._view.present_center_word('Short Break', 10)
                self._trigger(marker.PAUSE_END, wait=True)
        
        # Close logfile and exit the feedback main loop
        self.close_log()
        self.quit()
        

    def prepare(self):
        """ This is a generator function. It is the same as a loop, but
        execution is always suspended at a yield statement. The argument
        of yield acts as the next iterator element. In this case, none
        is needed, as we only want to prepare the next stimulus and use
        yield to signal that we are finished.
        """      
        for n in range(0,len(self.stim_pres_seq),2):                      
            # s1-stimulus presentation                          
            self.image.set_file(self.stim_pres_seq[n])#, texture=VisionEgg.Textures.Texture(stim))
            self._trigger(self.S1, wait=True)
            self.image.set(on=True)
            yield 
            # s1-s2 interstimulus interval
            self.image.set(on=False)
            self._trigger(self.IVAL_S1_S2, wait=True)
            yield 
            # s2-stimulus presentation              
            self.image.set_file(self.stim_pres_seq[n+1])
            self.image.set(on=True)
            self._trigger(self.S2, wait=True)
            yield 
            # s2-s1 interstimulus interval
            self.image.set(on=False)
            self._trigger(self.IVAL_S2_S1, wait=True)
            yield 
    
    
    def create_stim_seq(self,nTrials=None):
        if nTrials == None:
            nTrials = self.nTrials_per_block
            
        # convert stimuls sequence to a stimulus sequence of image filenames
        self.stim_pres_seq = list()        
        for n in range(nTrials):
            if n%2==0: # alternate
                self.stim_pres_seq.append(self.std[random.randint(0,len(self.std)-1)])
            else:  
                self.stim_pres_seq.append(self.dev[random.randint(0,len(self.std)-1)])  
                        
                    
        
if __name__ == '__main__':
    vo = VisualOddballVE_CNV()
    #vo.__init__()
    vo.pre_mainloop()
    vo._mainloop()    
    #vo.run()

