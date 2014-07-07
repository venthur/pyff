#!/usr/bin/env python


# ODDBALL BASE CLASS from which all the subclasses inherit.
#
# Currently existing subclasses:
#     - AuditoryOddball
#     - VisualOddball
#     - TactileOddball
#
# Methods that have to be implemented by a subclass:
# - init:                       if some default settings should be changed
# - load_stimulus:              if stimuli are files (e.g. images, audio-files)    
# - get_predefined_stimuli:     if stimuli are created by a python module
# - start_stimulus:             determines how the stimulus presentation is started
# - stop_stimulus:              determines how the stimulus presentation is stopped
#
# NORMAL WORKFLOW:
# (1) prestimulus interval
# (2) stimulus interval (actual stimulus presentation can be shorter)
# (3) response interval
# (4) feedback interval
#
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

"""Base Class for Oddball Experiments."""

import random
import sys
import math
import os
import warnings
from scipy import *

import pygame

from FeedbackBase.MainloopFeedback import MainloopFeedback
from lib import marker
from lib import serialport

class Oddball(MainloopFeedback):
    
    STANDARD, DEVIANT = list(),list()    
    # standards have markers 10,11,12,... ; deviants 30,31,32,... (cf. get_stimuli())
    # if self.group_stim_markers==True, then there exist only two markers, one for
    # group standard (10), and one for group deviant (20)
    RESP_STD, RESP_DEV = 1,2
    
    def init(self):        
        self.screen_pos = [100, 100, 640, 480]
        self.fullscreen = False
        self.FPS = 40
        self.nStim = 10
        self.nStim_per_block = 5        
        self.dev_perc = 0.1        
        self.countdown_from = 2
        self.show_standards = True
        self.give_feedback = True
        self.group_stim_markers = False
        self.dd_dist = 2    # no contraint if deviant-deviant distance is 0 (cf. oddball sequence)            
        
        self.DIR_DEV = ''
        self.DIR_STD= ''
        stimuli_opts = ['load', 'predefined']
        self.stimuli = stimuli_opts[1]
        
        # response options        
        self.rsp_key_dev = 'f'
        self.rsp_key_std = 'j' 
        response_opts = ['none', 'dev_only', 'both'] # none: subject should not press a key
                                                     # dev_only: subject should press only for deviants
                                                     # both: subject response for both stds and devs        
        self.response = response_opts[2]            

        # Durations of the different blocks
        self.feedback_duration, self.stim_duration = 300,  400      
        self.gameover_duration = 3000
        self.shortpauseDuration = 10000
        self.responsetime_duration = 100
        self.beforestim_ival = [200, 300]  # randomly between the two values
                
        # Feedback state booleans        
        self.gameover, self.responsetime = False, False
        self.countdown, self.firstStimTick = True, True
        self.beforestim, self.shortpause = False, False
        self.feedback = False
        
        # Init block time elapsed variables
        self.elapsed, self.stimElapsed, self.countdownElapsed = 0, 0, 0
        self.feedbackElapsed, self.shortpauseElapsed = 0, 0
        self.beforestimElapsed, self.responsetimeElapsed = 0, 0
        
        # Colour settings
        self.backgroundColor = (50, 50, 50)
        self.feedbackColor = (0, 150, 150)
        self.countdownColor = (200, 80, 118)
        self.fontColor = self.feedbackColor        
                
        self.responses = [0,0,0]
        self.last_response = ''
        self.stimuliShown = 0
        self.hitstr, self.missstr, self.falsestr = 'H: ', '  M: ', '  F: '
 
        self.serialtrigger = False
        self.serialport = serialport.SerialPort(13)
        self.send_parallel_bak = self.send_parallel
                                               
                                    
    def get_stimuli(self):
        if self.stimuli == 'load':              # load stimuli from files
            self.stds, self.devs = self.load_stimuli()
        elif self.stimuli == 'predefined':      # use predefined stimuli
            self.stds, self.devs = self.define_stimuli()
        else:
            raise Exception('Stimuli option unknown.')
        
        # create parallel port markers for deviants and standards
        [self.STANDARD.append(10+s) for s in range(len(self.stds))]
        [self.DEVIANT.append(30+d) for d in range(len(self.devs))]
            
        
    def load_stimuli(self):
        """
        Loads deviant and standard stimuli from files (in folders
        self.FIG_DIR_DEV and self.FIG_DIR_STD)
        """
        stds, devs = [], []
        if self.DIR_DEV == '':
            raise Exception('Directory containing deviant stimuli has to be defined.')        
        elif self.DIR_STD=='' and self.show_standards:
            raise Exception('Directory containing standard stimuli has to be defined.')
            
        print 'Loading stimuli....'
        for filename in os.listdir(self.DIR_STD):
            stds.append(self.load_stimulus(self.DIR_STD+'/'+filename))
        for filename in os.listdir(self.DIR_DEV):
            devs.append(self.load_stimulus(self.DIR_DEV+'/'+filename))
        print 'Done.'               
        return stds, devs

    
    def load_stimulus(self,filename):
        """
        Loads a stimulus from a file.
        """
        raise Exception('Method has to implemented by a subclass')
        
        
    def define_stimuli(self):
        """
        Creates standard and deviant stimuli.          
        """
        raise Exception('Method has to implemented by a subclass')
        

    def start_stimulus(self, stim):
        """
        Start the stimulus presentation.
        """
        raise Exception('Method has to implemented by a subclass')


    def stop_stimulus(self, stim):
        """
        Stop the stimulus presentation.
        """
        raise Exception('Method has to implemented by a subclass')


    def error_checking(self):
        """
        Check the settings for errors
        """
        if not self.show_standards:
            if self.response != 'dev_only':
                self.response = 'dev_only'
                warnings.warn('Standards not shown. Response option will be changed to ''dev_only''')        

                
    def pre_mainloop(self):
        """
        Sets up all the necessary components (e.g. pygame, stimuli, graphics) 
        to run the experiment.
        """
        self.send_parallel(marker.RUN_START)
        self.init_pygame()
        self.get_stimuli()
        self.error_checking()
        self.init_graphics()
        #self.init_run()
        self.gameover = False


    def on_interaction_event(self, data):
        self.logger.debug('interaction event')
        serial = data.get('serialtrigger', None)
        if serial is None:
            return
        if serial:
            self.logger.debug('using serial port')
            self.send_parallel = self.serialport.send
        else:
            self.logger.debug('using parallel port')
            self.send_parallel = self.send_parallel_bak


    def post_mainloop(self):
        """
        Sends end marker to parallel port and quits pygame.
        """
        self.send_parallel(marker.RUN_END)
        pygame.quit()        


    def tick(self):
        self.process_pygame_events()
        pygame.time.wait(10)
        self.elapsed = self.clock.tick(self.FPS)


    def pause_tick(self):
        self.do_print("Pause", self.fontColor, self.size / 6)


    def play_tick(self):
        
        if self.feedback:
            #print 'in feedback'
            self.feedback_tick()
        elif self.countdown:
            #print 'in countdown'
            self.countdown_tick()
        elif self.gameover:
            #print 'in gameover'
            self.gameover_tick()
            self.on_stop()
        elif self.shortpause:
            #print 'in pause'
            self.short_pause_tick()        
        elif self.responsetime:
            #print 'in response'
            self.responsetime_tick()
        elif self.beforestim:
            #print 'in beforestim'
            self.beforestim_tick()
        else:            
            #print 'in stim'
            self.stim_tick()

            
    def stim_tick(self):
        """
        Called repeatedly during the stimulus presentation.
        """
        self.stimElapsed += self.elapsed
        if self.firstStimTick:    
            self.firstStimTick = False    
            self.draw_initial()
            self.timeAfterStim = 0
            if self.stim_sequence[self.stimuliShown%self.nStim_per_block]==1:
                self.stim, idx = self.get_deviant()                
                self.send_stim_marker(self.DEVIANT,idx)
                self.isdeviant = True
                self.start_stimulus(self.stim)        
            else:                
                self.isdeviant = False
                if self.show_standards:
                    self.stim, idx = self.get_standard()
                    self.send_stim_marker(self.STANDARD,idx)
                    self.start_stimulus(self.stim)  
                else:
                    self.stim = None
                    self.send_parallel(self.STANDARD)            
        
        # check if stimulus duration is over
        if self.stimElapsed>self.stim_duration:
            self.firstStimTick = True
            if self.responsetime_duration != 0:
                self.responsetime = True
            self.stimElapsed = 0    
            self.stimuliShown += 1        
            if self.stim:
                self.stop_stimulus(self.stim)
            # pause?
            if self.stimuliShown % self.nStim_per_block == 0:
                self.shortpause = True
            # game over?
            if self.stimuliShown >= self.nStim:
                self.gameover = True


    def send_stim_marker(self, markerlist, idx):
        """
        Sends a stimulus marker (standard or deviant) to the parallel port.  
        """
        if not idx or self.group_stim_markers:
            self.send_parallel(markerlist[0])
        else:
            self.send_parallel(markerlist[idx])


    def get_deviant(self):        
        if len(self.devs)>1:
            idx = random.randint(0,len(self.devs)-1)
        else:
            idx = 0                        
        return self.devs[idx], idx
        
        
    def get_standard(self):
        if len(self.stds)>1:
            idx = random.randint(0,len(self.stds)-1)
        else:
            idx = 0
        return self.stds[idx], idx        
    
    
    def responsetime_tick(self):
        """
        Called between stimulus presentation and feedback.
        """
        self.responsetimeElapsed += self.elapsed
        
        if self.responsetimeElapsed >= self.responsetime_duration:
            self.responsetime = False
            self.responsetimeElapsed = 0
            self.evaluate_response()
            
            
    def evaluate_response(self):                    
        
        if self.give_feedback and (self.show_standards or self.isdeviant):
            if self.last_response == 'Hit':
                self.responses[0] += 1
            elif self.last_response == 'False':
                self.responses[2] += 1
            else:                 # no response --> miss
                self.responses[1] += 1
                self.last_response = 'Miss'
            self.feedback = True
        else:
            self.last_response = ''
            if self.beforestim_duration != 0:
                self.beforestim = True
            
        
    def feedback_tick(self):
        """
        Gives feedback about the last response.
        """ 
        if self.feedbackElapsed == 0:                  
            self.show_feedback()
            
        self.feedbackElapsed += self.elapsed
        
        if self.feedbackElapsed >= self.feedback_duration:
            self.feedbackElapsed = 0
            self.last_response = ''
            self.feedback = False
            self.beforestim = True   
            self.draw_initial()             

    
    def show_feedback(self):
        """
        Draws the feedback on the screen.
        """
        self.screen.blit(self.background, self.backgroundRect)
        #s = self.hitstr + str(self.responses[0]) + self.missstr + str(self.responses[1]) + self.falsestr + str(self.responses[ - 1])        
        self.do_print(self.last_response, self.feedbackColor)        

    
    def short_pause_tick(self):
        """
        One tick of the short pause loop.
        """
        if self.shortpauseElapsed == 0:
            self.send_parallel(marker.PAUSE_START)
        
        self.shortpauseElapsed += self.elapsed
        
        if self.shortpauseElapsed >= self.shortpauseDuration:
            self.shortpause = False
            self.shortpauseElapsed = 0
            self.countdown = True
            self.send_parallel(marker.PAUSE_END)
            return
        
        self.do_print("Short Break...", self.fontColor, self.size / 10)


    def countdown_tick(self):
        """
        One tick of the countdown loop.
        """        
        # start countdown
        if self.countdownElapsed == 0:
            self.send_parallel(marker.COUNTDOWN_START)
            self.draw_initial()
            # initialize stimulus sequence for the next block according to the deviant probability
            n = min(self.nStim_per_block,self.nStim)
            self.stim_sequence = self.contrained_oddball_sequence(n,self.dev_perc,self.dd_dist)
        
        self.countdownElapsed += self.elapsed 
               
        # stop countdown
        if self.countdownElapsed >= (self.countdown_from) * 1000:
            self.send_parallel(marker.COUNTDOWN_END)
            self.countdown = False
            self.countdownElapsed = 0
            self.beforestim = True               
            self.init_graphics()
            return        
        
        # draw countdown on screen
        t = ((self.countdown_from + 1) * 1000 - self.countdownElapsed) / 1000
        self.do_print(str(t), self.countdownColor, self.size / 4)
        
    
    def beforestim_tick(self):
        """
        Called directly before stimulus presentation.
        """
        if self.beforestimElapsed == 0:
            r = random.random()
            self.beforestim_duration = r*self.beforestim_ival[0] + (1-r)*self.beforestim_ival[1]
            
        self.beforestimElapsed += self.elapsed
        
        if self.beforestimElapsed >= self.beforestim_duration:
            self.beforestim = False
            self.beforestimElapsed = 0
    
        
    def gameover_tick(self):
        """
        One tick of the game over loop.
        """
        self.draw_initial()
        if self.give_feedback:
            if self.show_standards:
                s = self.hitstr + str(self.responses[0]) + self.missstr + str(self.responses[1]) + self.falsestr + str(self.responses[ - 1])
            else:
                s = self.hitstr + str(self.responses[0]) + self.missstr + str(self.responses[1])
            self.do_print(s, self.fontColor, self.size / 10)
        pygame.time.wait(self.gameover_duration)
        
       
    def do_print(self, text, color, size=None, center=None, superimpose=True):
        """
        Print the given text in the given color and size on the screen.
        """
        if not color:
            color = self.fontColor
        if not size:
            size = self.size / 10
        if not center:
            center = self.screen.get_rect().center

        font = pygame.font.Font(None, size)
        if not superimpose:
            self.screen.blit(self.background, self.backgroundRect)            
        surface = font.render(text, 1, color,self.backgroundColor)    
        self.screen.blit(surface, surface.get_rect(center=center))
        pygame.display.update()
                
    def init_graphics(self):
        """
        Initialize the surfaces and fonts.
        """
        self.screen = pygame.display.get_surface()
        self.size = min(self.screen.get_height(), self.screen.get_width())
        
        # init background
        self.background = pygame.Surface((self.screen_pos[2], self.screen_pos[3]))
        self.background = self.background.convert()
        self.backgroundRect = self.background.get_rect(center=self.screen.get_rect().center)
        self.background.fill(self.backgroundColor)
        self.draw_initial()
    
    def draw_initial(self):
        """
        Draw the default screen layout.
        """            
        self.screen.blit(self.background, self.backgroundRect)
        pygame.display.update()
        
    def process_pygame_events(self):
        """
        Process the pygame event queue.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and self.response!='none':
                if self.responsetime or self.stimElapsed!=0:
                    if event.unicode == unicode(self.rsp_key_dev):
                        self.send_parallel(self.RESP_DEV)
                        if self.isdeviant:
                            self.last_response = 'Hit'
                        else:
                            self.last_response = 'False'
                    elif event.unicode == unicode(self.rsp_key_std) and self.response=='both':
                        self.send_parallel(self.RESP_STD)
                        if self.isdeviant:
                            self.last_response = 'False'
                        else:
                            self.last_response = 'Hit'
                            
    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screen_pos[0], self.screen_pos[1])        
        pygame.init()
        pygame.display.set_caption('Oddball')
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screen_pos[2], self.screen_pos[3]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screen_pos[2], self.screen_pos[3]), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

    def contrained_oddball_sequence(self, N, dev_perc, dd_dist=0):    
        """
        N:          total number of trials
        perc_dev:   percentage of deviants
        dd_dist:    constraint variable: minimal number of standards between two deviants 
                   (default: no contraint (=0))
        """
    
        devs_to_be_placed= round(N*dev_perc)
        if devs_to_be_placed+(devs_to_be_placed-1)*dd_dist>N:
            solve_prob = 'Increase the number of trials, or decrease the percentage of deviants or the minimal dev-to-dev-distance.' 
            raise Exception('Oddball sequence constraints cannot be fullfilled. ' + solve_prob)
    
        devs = -1
        while round(N*dev_perc) != devs:
            sequence= zeros((N,1));
            devs_to_be_placed= round(N*dev_perc)
            ptr = 0
            while ptr < N:        
                togo= N-ptr
                prob= devs_to_be_placed/floor(togo/2)        
                if random.random() < prob:
                    sequence[ptr] = 1
                    devs_to_be_placed = devs_to_be_placed - 1
                    ptr = ptr + dd_dist
                ptr= ptr +  1
            devs = sum(sequence)
        #print sequence
        return sequence
    
    def create_list(self, nStim, stim_perc):
        """ 
        Creates a randomly shuffled list with numbers ranging from 0-(nStim-1)
        The percentages of the numbers occuring are given by the list stim_perc
        """
        list = [];
        for n in range(len(stim_perc)):
            list.extend([n] * int(nStim*stim_perc[n]))
        random.shuffle(list)
        return list
    
        
