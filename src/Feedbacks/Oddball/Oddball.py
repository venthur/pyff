#!/usr/bin/env python


# ODDBALL BASE CLASS from which all the subclasses inherit.
#
#
# Currently existing subclasses:
#     - AuditoryOddball
#     - VisualOddball
#     - TactileOddball
#
# Methods that have to be implemented by a subclass
# - init:                       if some default settings should be changed
# - load_stimulus:              if stimuli are files (e.g. images, audio-files)    
# - get_predefined_stimuli:     if stimuli are created by a python module
# - present_stimulus:           determines how the stimuli are presented
#
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

import pygame

from FeedbackBase.MainloopFeedback import MainloopFeedback

class Oddball(MainloopFeedback):
    
    RUN_START, RUN_END = 252, 253
    COUNTDOWN_START, COUNTDOWN_END = 40,41
    STANDARD, DEVIANT = 10,20
    RESP_STD, RESP_DEV = 1,2
    SHORTPAUSE_START, SHORTPAUSE_END = 249, 250
    
    def init(self):
        self.screen_pos = [100, 100, 640, 480]
        self.FPS = 40
    
        self.DIR_DEV = ''
        self.DIR_STD= ''
        self.stimuli = 'predefined'
        self.get_stimuli()
        
        self.nStim = 100
        self.pause_after = 50        
        self.dev_prob = 0.1        
        self.countdown_from = 2
        self.show_standards = True
        self.give_feedback = True
        
        # response options        
        self.rsp_key_dev = 'f'
        self.rsp_key_std = 'j' 
        self.response_opts = ['none', 'dev_only', 'both'] # none: subject should not press a key
                                                          # dev_only: subject should press only for deviants
                                                          # both: subject reponse for both stds and devs        
        self.response = self.response_opts[2]            

        # Durations of the different blocks
        self.feedback_duration, self.stim_duration = 200,  500      
        self.gameover_duration = 3000
        self.responsetime_duration = 0 
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
                
        self.responses = [0,0,0]
        self.last_response = ''
        self.stimuliShown = 0
        self.hitstr, self.missstr, self.falsestr = 'H: ', '  M: ', '  F: '

        if not self.show_standards:
            if self.response != 'dev_only':
                self.response = 'dev_only'
                warnings.warn('Standards not shown. Response option will be changed to ''dev_only''')
                                                    
                                    
    def get_stimuli(self):
        if self.stimuli == 'load':              # load stimuli from files
            self.load_stimuli()
        elif self.stimuli == 'predefined':      # use predefined stimuli
            self.define_stimuli()
        else:
            raise Exception('Stimuli option unknown.')
    
        
    def load_stimuli(self):
        """
        Loads deviant and standard stimuli from files (in folders
        self.FIG_DIR_DEV and self.FIG_DIR_STD)
        """
        self.stds, self.devs = [], []        
        for filename in os.listdir(self.DIR_STD):
            self.stds.append(load_stimulus(self.DIR_STD+filename))
        for filename in os.listdir(self.DIR_DEV):
            self.devs.append(load_stimulus(self.DIR_DEV+filename))  
        nDevs = length(self.devs)                  
    
    
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
        

    def present_stimulus(self):
        """
        Draw the stimulus onto the screen.
        """
        raise Exception('Method has to implemented by a subclass')

                
    def pre_mainloop(self):
        self.send_parallel(self.RUN_START)
        self.init_pygame()
        self.init_graphics()
        #self.init_run()
        self.gameover = False


    def post_mainloop(self):
        self.send_parallel(self.RUN_END)
        pygame.quit()        


    def tick(self):
        self.process_pygame_events()
        pygame.time.wait(10)
        self.elapsed = self.clock.tick(self.FPS)


    def pause_tick(self):
        self.do_print("Pause", self.fontColor, self.size / 6)


    def play_tick(self):
        
        if self.countdown:
            #print 'in countdown'
            self.countdown_tick()
        elif self.gameover:
            #print 'in gameover'
            self.gameover_tick()
        elif self.shortpause:
            #print 'in pause'
            self.short_pause_tick()
        elif self.feedback:
            #print 'in feedback'
            self.feedback_tick()
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
        Called repeatedly during the stimulus presentation
        """
        self.stimElapsed += self.elapsed
        if self.firstStimTick:    
            self.firstStimTick = False    
            self.draw_initial()
            self.timeAfterStim = 0
            if self.stim_sequence[self.stimuliShown]==0:
                self.send_parallel(self.DEVIANT)
                self.isdeviant = True
                self.stim = self.get_deviant()
                self.present_stimulus()        
            else:
                self.send_parallel(self.STANDARD)
                self.isdeviant = False
                if self.show_standards:
                    self.stim = self.get_standard()
                    self.present_stimulus()        
                
        if self.stimElapsed>self.stim_duration:
            self.firstStimTick = True
            self.responsetime = True
            self.stimElapsed = 0
            self.stimuliShown += 1
            self.draw_initial()


    def get_deviant(self):
        r = random.randint(0,len(self.devs)-1)
        return self.devs[r]
        
        
    def get_standard(self):
        r = random.randint(0,len(self.stds)-1)
        return self.stds[r]        
    
    
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
        if self.last_response == 'Hit':
            self.responses[0] += 1
        elif self.last_response == 'False':
            self.responses[2] += 1
        else:                 # no response --> miss
            self.responses[1] += 1
            self.last_response = 'Miss'            
        
        if self.give_feedback and (self.show_standards or self.isdeviant):
            self.feedback = True
        else:
            self.last_response = ''
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
                
            if self.stimuliShown % self.pause_after == 0:
                self.shortpause = True
            if self.stimuliShown >= self.nStim:
                self.gameover = True
            return

    
    def show_feedback(self):
        self.screen.blit(self.background, self.backgroundRect)
        #s = self.hitstr + str(self.responses[0]) + self.missstr + str(self.responses[1]) + self.falsestr + str(self.responses[ - 1])        
        self.do_print(self.last_response, self.feedbackColor)        

    
    def short_pause_tick(self):
        """
        One tick of the short pause loop.
        """
        if self.shortpauseElapsed == 0:
            self.send_parallel(self.SHORTPAUSE_START)
        
        self.shortpauseElapsed += self.elapsed
        
        if self.shortpauseElapsed >= self.pauseDuration:
            self.shortpause = False
            self.shortpauseElapsed = 0
            self.countdown = True
            self.send_parallel(self.SHORTPAUSE_END)
            return
        
        self.do_print("Short Break...", self.fontColor, self.size / 10)


    def countdown_tick(self):
        """
        One tick of the countdown loop.
        """        
        # start countdown
        if self.countdownElapsed == 0:
            self.send_parallel(self.COUNTDOWN_START)
            self.draw_initial()
            # initialize stimulus sequence for the next block according to the deviant probability
            self.stim_sequence = [1] * int(self.pause_after)
            self.stim_sequence[0:int(self.dev_prob*self.pause_after)] = [0] * int(self.dev_prob*self.pause_after)
            random.shuffle(self.stim_sequence)
            print self.stim_sequence            
        
        self.countdownElapsed += self.elapsed 
               
        # stop countdown
        if self.countdownElapsed >= (self.countdown_from) * 1000:
            self.send_parallel(self.COUNTDOWN_END)
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
        self.draw_all(False)
        self.do_print("(%i : %i, %i)" % (self.reponses[0], self.reponses[1], self.reponses[2]), self.feedbackColor, self.size / 10)
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
        surface = font.render(text, 1, color, self.backgroundColor)    
        self.screen.blit(surface, surface.get_rect(center=center))
        pygame.display.update()
        #if superimpose:
        #    pygame.display.update(surface.get_rect(center=center))

                
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
        self.screen = pygame.display.set_mode((self.screen_pos[2], self.screen_pos[3]), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

