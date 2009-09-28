#!/usr/bin/env python

# NOTE: This class makes use of the python module 'audiere' (http://pyaudiere.org/)
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

"""Class for Auditory Oddball Experiments."""

import audiere

from Feedbacks.Oddball import Oddball

class AuditoryOddball(Oddball.Oddball):
    
    def init(self):        
        super(AuditoryOddball,self).init()
        self.DIR_DEV = 'C:/stim_test/dev'    
        self.DIR_STD = 'C:/stim_test/std'
        self.stimuli = 'predefined'
        self.nStim = 15
        self.au = audiere.open_device()  
        self.dev_perc = 0.3  
        
    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file and returns it.
        """
        return self.au.open_file(filename)
        
    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.          
        """        
        dev1 = self.au.create_tone(500)
        std1 = self.au.create_tone(700)                
        return [std1], [dev1]

    def start_stimulus(self, stim):
        """
        Start audio file.
        """           
        stim.play()
    
    def stop_stimulus(self, stim):
        """
        Stop audio file.
        """           
        stim.pause()  #stim.stop()
            
if __name__ == '__main__':
    vo = AuditoryOddball()
    vo.on_init()
    vo.on_play()        