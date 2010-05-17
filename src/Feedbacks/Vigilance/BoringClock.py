# BoringClock.py -
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

"""
A clockwork task for measuring sustatined attention/vigilance, adapted
from Mackworth's (1957) very monotonous Clock Test. The task is to follow 
a dot moving in discrete steps on a circular arrangement of open circles.
At some (rare) occassions, the dot skips one step. A button has to be pressed
on these occasions.  

Mackworth, N.H. (1957). Some factors affecting vigilance.
Advancement of Science, 53, 389-393.
"""

"""
Triggers: 10,11,12... for each position on the circle
Jump: 8
Button press: 9
"""

import sys,os,random,time
import pygame
from FeedbackBase.MainloopFeedback import MainloopFeedback
from lib.P300Layout import CircularLayout

class BoringClock(MainloopFeedback):
    
    # Triggers
    RUN_START, RUN_END = 252,253
    COUNTDOWN_START, COUNTDOWN_END = 200,201
    JUMP,BUTTON = 8,9
    
    # States during running
    COUNTDOWN, STIM, FIN = 1,2,3
    
    def init(self):
        random.seed()
        self.nEl = 24                   # Nr of elements on the circle
        self.showClock = True           # show dot positions
        self.nClockTicks = 100          # Total number of clock ticks
        self.nJumps = 5                 # Total number of jumps among the clock ticks (number should be a divisor of nClockTicks) 
        self.button = pygame.K_KP0      # Which button has to be pressed
        self.minDist = 10               # Minimum distance between successive jumps 
                                        # (and also minimum distance between begin and end of sequence) 
        # Timing 
        self.fps = 30                   # Frames-per-second
        self.stimTime = 30               # How long the stimulus is displayed (in frames)
        self.nCountdown = 1             # N of secs to count down
        # Triggers
        self.triggers = range(10,10+self.nEl) # 10,11,12,...
        self.triggerAdd = 20            # If current symbol matches the nth back symbol, this number is added to the trigger
        # Auditory settings
        self.auditoryFeedback = False       # Auditory feedback provided
        # Graphical settings
        self.bgcolor = 0, 0, 0
        self.colDot = 200,200,200       # Color of moving dot
        self.colClock = 55,55,55     # Color of clock positions
        self.screenPos = [200,200,600,600]
        self.fullscreen = False
        self.radiusDisplay = 200        # Radius of circular arrangement
        self.dotRadius = 10              # Radius of each element
        self.size = 100                 # Size of letters (eg countdown) 
        
    def _init_pygame(self):

        # Initialize pygame, open screen and fill screen with background color 
        #os.environ['SDL_VIDEODRIVER'] = self.video_driver   # Set video driver
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screenPos[0], self.screenPos[1])        
        pygame.init()
        pygame.display.set_caption('BoringClock')
        if self.fullscreen: 
            opts = pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((self.screenPos[2],self.screenPos[3]),opts)
        else: 
            self.screen = pygame.display.set_mode((self.screenPos[2],self.screenPos[3]))
        self.background = pygame.Surface((self.screenPos[2],self.screenPos[3])) 
        self.background.fill(self.bgcolor)
        self.background_rect = self.background.get_rect(center = (self.screenPos[2]/2,self.screenPos[3]/2) )
        self.screen.blit(self.background,self.background_rect)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, self.size)
        # init sound engine
        pygame.mixer.init()
        # Prepare antialiased dot and clock-dot
        self.dot = pygame.Surface((4 * self.dotRadius, 4 * self.dotRadius))
        self.clockdot = pygame.Surface((4 * self.dotRadius, 4 * self.dotRadius))
        self.dot.fill(self.bgcolor)
        self.clockdot.fill(self.bgcolor)
        pygame.draw.circle(self.dot,self.colDot, (2*self.dotRadius, 2*self.dotRadius), 2*self.dotRadius)
        pygame.draw.circle(self.clockdot,self.colClock, (2*self.dotRadius, 2*self.dotRadius), 2*self.dotRadius)
        self.dot = pygame.transform.smoothscale(self.dot, (2*self.dotRadius,2*self.dotRadius))
        self.clockdot = pygame.transform.smoothscale(self.clockdot, (2*self.dotRadius,2*self.dotRadius))
        # Prepare coordinates of clock dots
        cl = CircularLayout.CircularLayout(nr_elements=self.nEl,radius=self.radiusDisplay)
        self.positions = []
        for i in range(self.nEl):
            x = cl.positions[i][0] + self.screenCenter[0]
            y = cl.positions[i][1] + self.screenCenter[1]
            self.positions.append( (x,y) )
        

    def pre_mainloop(self):
        self.send_parallel(self.RUN_START)
        time.sleep(1)
        """ Internal variables """
        self.currentPos = 0           # Current position in sequence
        self.clockPos = 0             # Current position of clock
        self.currentTick = 0            # Tick counter
        self.sequence = [0]*self.nClockTicks    # Sequence of presented symbols
        self.screenCenter = (self.screenPos[2]/2,self.screenPos[3]/2)
        # States
        self.state = self.COUNTDOWN
        self.state_finished = False
        self.responseGiven = 0
        self.random_sequence()
        # Init graphics and sound
        self._init_pygame()
        if self.auditoryFeedback:
            dir = os.path.dirname(sys.modules[__name__].__file__) # Get current dir
            self.sound = pygame.mixer.Sound(dir + "/sound18.wav")
        print self.sequence
               
    def tick(self):
        # If last state is finished, proceed to next state
        if self.state_finished:
            if self.state == self.COUNTDOWN:
                self.state = self.STIM
            elif self.state == self.STIM:
                if self.currentPos == self.nClockTicks:
                    # finito
                    self.on_stop()
                    self.state = self.FIN
            self.currentTick = 0        # Reset tick count
            self.state_finished = False

    def play_tick(self):
        if self.checkWindowFocus():
            state = self.state
            if state == self.COUNTDOWN:
                self.countdown()
            elif state == self.STIM:
                self.stim()
            # Keep running at the number of fps specified
            self.clock.tick(self.fps)

    def pause_tick(self):
            txt = self.font.render("PAUSE",self.ANTIALIAS,self.color)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.clock.tick(self.fps)
            
    def countdown(self):
        if self.currentTick/self.fps == self.nCountdown:
            self.send_parallel(self.COUNTDOWN_END)
            # Finished counting, draw background
            self.state_finished = True
            self.screen.blit(self.background,self.background_rect)
            pygame.display.update()
        elif self.currentTick % self.fps == 0:
            if self.currentTick == 0:        # the very first tick
                self.send_parallel(self.COUNTDOWN_START)
            # New number
            count = self.nCountdown - (self.currentTick+1)/self.fps
            txt = self.font.render(str(count),1,self.colDot)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.currentTick += 1
        else:
            # Keep drawing the same number
            count = self.nCountdown - self.currentTick/self.fps
            txt = self.font.render(str(count),1,self.colDot)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.currentTick += 1

    def drawStim(self):
        """
        Draws the clock and the dot
        """
        self.screen.blit(self.background,self.background_rect)
        # Draw the clock
        if self.showClock:                  
            for ii in range(self.nEl):
                clockrect = self.clockdot.get_rect(center = self.positions[ii] )
                self.screen.blit(self.clockdot, clockrect)
        # Draw dot
        dotrect = self.dot.get_rect(center = self.positions[self.clockPos] )
        self.screen.blit(self.dot, dotrect)
        pygame.display.update()

             
    def stim(self):
        if self.currentTick == 0:
            # Check if we have to jump
            if self.sequence[self.currentPos]==0:
                # send normal trigger
                self.send_parallel(self.triggers[self.clockPos])
                self.clockPos +=1
            else:
                # send jump trigger
                self.send_parallel(self.JUMP)
                self.clockPos +=2
            # Reset clock tick after one cycle
            self.clockPos = self.clockPos % self.nEl
            # Draw symbol
            self.drawStim()
            self.currentTick += 1
        elif self.currentTick == self.stimTime:
            # Finished
            self.drawStim()
            self.state_finished = True
            self.currentPos += 1
        else:
            self.drawStim()
            self.currentTick += 1
    
    def checkInput(self):
        """ Time window within which response is to be given """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_stop()
                elif event.key in (pygame.K_KP1,pygame.K_KP2) and not self.responseGiven:
                    if self.currentStim >= self.n:   # After the first n stimuli: Waiting for responses
                        # Process button press                    
                        c = self.currentStim
                        isSame = self.sequence[c]==self.sequence[c-self.n]
                        wrongRight = (event.key == pygame.K_KP1 and isSame) or (event.key == pygame.K_KP2 and not isSame)
                        if wrongRight == 1:
                            self.send_parallel(self.RICHTIG)
                        else:
                            self.send_parallel(self.FALSCH)
                            if self.auditoryFeedback:
                                self.sound.play()
                        self.responseGiven = 1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                c = self.currentStim
                isSame = self.sequence[c]==self.sequence[c-self.n]
                # 1: left mouse button   3: right mouse button
                wrongRight = (event.button == 1 and isSame) or (event.button==3 and not isSame)
                if wrongRight == 1:
                    self.send_parallel(self.RICHTIG)
                else:
                    self.send_parallel(self.FALSCH)
                    if self.auditoryFeedback:
                        self.sound.play()
                self.responseGiven = 1
                    
    def post_mainloop(self):
        if self.auditoryFeedback:
            self.sound = None
            pygame.mixer.quit()
        pygame.quit()
        self.send_parallel(self.RUN_END)
        
    def random_sequence(self):
        """
        Generates a random sequence of jumps by partitioning the whole
        clock-tick sequence into equi-sized halves and then placing a 
        jump within each partition.
        """
        nPartition = self.nClockTicks / self.nJumps     # size of each partition (containing one jump each)
        # First partition
        idx = random.randint(self.minDist,nPartition-1)
        self.sequence[idx] = 1
        # Mid partitions
        for ii in range(1,self.nJumps-1):
            dist = nPartition-1-idx       # distance to next partition
            if self.minDist>dist:
                idx = random.randint(self.minDist-dist,nPartition-1)
            else:
                idx = random.randint(0,nPartition-1)
            self.sequence[nPartition*ii+idx] = 1
        # Last partition
        dist = nPartition-1-idx       # distance to next partition
        if self.minDist>dist:
            idx = random.randint(self.minDist-dist,nPartition-1-self.minDist)
        else:
            idx = random.randint(0,nPartition-1-self.minDist)
        self.sequence[nPartition*(self.nJumps-1)+idx] = 1
            
    
    def checkWindowFocus(self):
        """
        Return true if pygame window has focus. Otherwise display text
        and return false.
        """
        pygame.event.get()
        if not pygame.key.get_focused():
            txt = self.font.render("Click to start",1,self.colDot)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            return False
        return True
       
        
    
if __name__ == "__main__":
    a = BoringClock()
    a.on_init()
    a.on_play()
