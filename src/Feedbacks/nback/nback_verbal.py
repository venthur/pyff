# nback_verbal.py -
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
A verbal n-back task. A sequence of symbols is successively presented 
on the screen. The participant's task is to indicate via a button press
(keyboard arrows or mouse button)
whether the current symbol matches the nth (e.g., first, second, or third)
symbol back in time.
"""

"""
Triggers: 10,11,12... for the symbols
+20, that is, 30,31,32 ... when it is a match with the n-th precursor
"""

import sys,os,random,time
import pygame
from FeedbackBase.MainloopFeedback import MainloopFeedback

class nback_verbal(MainloopFeedback):
    
    # Triggers
    RUN_START, RUN_END = 252,253
    COUNTDOWN_START, COUNTDOWN_END = 200,201
    FALSCH , RICHTIG = 7,8      # Response markers
    
    # States during running
    # First stimulus is shown, and after pre-response time
    # response is to be entered
    COUNTDOWN, STIM, PRE_RESPONSE, RESPONSE = 1,2,3,4
    
    # Antialising with the text
    ANTIALIAS = 1
        
    def init(self):
        random.seed()
        self.symbols = "ABC"
        #self.symbols = "BDFHJLNPRTVX"       # every 2nd letter starting from B (less easy to remember clear ordering)
        self.nMatch = 1                 # Number of nth matches for each symbol (should be less than half of nOccur)
        self.nOccur = 3                 # Total number of occurences of each symbol
        self.n = 1                      # Current symbol is matched with the nth symbol back
        # Timing 
        self.fps = 30                   # Frames-per-second
        self.stimTime = 2               # How long the stimulus is displayed (in frames)
        self.preResponseTime = 14        # How long to wait before response is accepted 
        self.responseTime = 10           # Time window for giving a response
        self.nCountdown = 1             # N of secs to count down
        self.auditoryFeedback = True       # Auditory feedback provided
        # Triggers
        self.triggers = range(10,10+len(self.symbols)) # 10,11,12,...
        self.triggerAdd = 20            # If current symbol matches the nth back symbol, this number is added to the trigger
        # Auditory settings
        #self.auditoryFeedback = False   # If yes, gives a beep when a wrong response is given
        # Graphical settings
        self.bgcolor = 0, 0, 0
        self.screenPos = [200,200,400,400]
        self.fullscreen = False
        self.color = 255,255,255        # Color of symbol
        self.size = 80                  # Size of symbol 

    def _init_pygame(self):
        # Initialize pygame, open screen and fill screen with background color 
        #os.environ['SDL_VIDEODRIVER'] = self.video_driver   # Set video driver
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screenPos[0], self.screenPos[1])        
        pygame.init()
        pygame.display.set_caption('N-Back')
        if self.fullscreen: 
            #use opts = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN to use doublebuffer and vertical sync
            opts = pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((self.screenPos[2],self.screenPos[3]),opts)
        else: 
            self.screen = pygame.display.set_mode((self.screenPos[2],self.screenPos[3]))
        self.background = pygame.Surface((self.screenPos[2],self.screenPos[3])) 
        self.background.fill(self.bgcolor)
        self.background_rect = self.background.get_rect(center = (self.screenPos[2]/2,self.screenPos[3]/2) )
        self.screen.blit(self.background,self.background_rect)
        self.clock = pygame.time.Clock()
        #pygame.mouse.set_visible(False)
        self.font = pygame.font.Font(None, self.size)
        # init sound engine
        pygame.mixer.init()

    def pre_mainloop(self):
        self.send_parallel(self.RUN_START)
        self._init_pygame()
        time.sleep(2)
        """ Internal variables """
        self.currentTick = 0            # Tick counter
        self.currentStim = 0            # Current number of stimulus    
        self.nSym = len(self.symbols)   # Number of symbols
        self.nStim = int(self.nSym*self.nOccur)  # Total number of stimuli
        self.sequence = [None]*self.nStim    # Sequence of presented symbols
        self.screenCenter = (self.screenPos[2]/2,self.screenPos[3]/2)
        # States
        self.state = self.COUNTDOWN
        self.state_finished = False
        self.responseGiven = 0
        self.random_sequence()
        dir = os.path.dirname(sys.modules[__name__].__file__) # Get current dir
        if self.auditoryFeedback:
            self.sound = pygame.mixer.Sound(dir + "/sound18.wav")
        
         
    def tick(self):
        # If last state is finished, proceed to next state
        if self.state_finished:
            if self.state == self.COUNTDOWN:
                self.state = self.STIM
            elif self.state == self.STIM:
                self.state  = self.PRE_RESPONSE
            elif self.state == self.PRE_RESPONSE:
                self.state = self.RESPONSE
            elif self.state == self.RESPONSE:
                self.responseGiven = 0
                if self.currentStim == self.nStim:
                    self.on_stop()
                else:
                    self.state = self.STIM
            self.currentTick = 0        # Reset tick count
            self.state_finished = False

    def play_tick(self):
        if self.checkWindowFocus():
            state = self.state
            if state == self.COUNTDOWN:
                self.countdown()
            elif state == self.STIM:
                self.stim()
            elif state == self.PRE_RESPONSE:
                self.pre_response()
            elif state == self.RESPONSE:
                self.response()
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
            txt = self.font.render(str(count),self.ANTIALIAS,self.color)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.currentTick += 1
        else:
            # Keep drawing the same number
            count = self.nCountdown - self.currentTick/self.fps
            txt = self.font.render(str(count),self.ANTIALIAS,self.color)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.currentTick += 1
                          
    def stim(self):
        if self.currentTick == 0:
            # Startup: send trigger
            currentSymbol = self.sequence[self.currentStim]
            if self.currentStim >= self.n:  # passed already more than n symbols
                isSame = currentSymbol==self.sequence[self.currentStim-self.n]
            else:
                isSame = False
            symbolIdx = self.symbols.find(currentSymbol) 
            trigger = self.triggers[symbolIdx]
            if isSame:
                trigger += self.triggerAdd
            self.send_parallel(trigger)
            # Draw symbol
            symbol = self.sequence[self.currentStim] 
            txt = self.font.render(symbol,self.ANTIALIAS,self.color)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.currentTick += 1
        elif self.currentTick == self.stimTime:
            # Finished
            self.screen.blit(self.background,self.background_rect)
            pygame.display.update()
            self.state_finished = True
        else:
            # Draw symbol
            symbol = self.sequence[self.currentStim] 
            txt = self.font.render(symbol,self.ANTIALIAS,self.color)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            self.currentTick += 1
    
    def pre_response(self):
        if self.currentTick == self.preResponseTime:
            # Finished
            self.screen.blit(self.background,self.background_rect)
            pygame.display.update()
            self.state_finished = True
        else:
            # Draw background
            self.screen.blit(self.background,self.background_rect)
            pygame.display.update()
            self.currentTick += 1
    
    def response(self):
        """ Time window within which response is to be given """
        if self.currentTick == self.responseTime:
            # Finished
            self.screen.blit(self.background,self.background_rect)
            pygame.display.update()
            self.state_finished = True
            self.currentStim += 1
        else:
            # Check pygame events incl button presses
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
                        
            # Draw background
            self.screen.blit(self.background,self.background_rect)
            pygame.display.update()
            self.currentTick += 1


    def post_mainloop(self):
        if self.auditoryFeedback:
            self.sound = None
            pygame.mixer.quit()
        pygame.quit()
        self.send_parallel(self.RUN_END)
        
    def random_sequence(self):
        # 1. Place all n-th matches randomly
        for symIdx in range(self.nSym):
            sym = self.symbols[symIdx] 
            for matIdx in range(self.nMatch):
                idx = []
                # Get indices of free space
                for i in range(self.nStim-self.n):
                    if (self.sequence[i] is None) and (self.sequence[i+self.n] is None):
                        idx.append(i)
                if not idx:
                    print("Error: Could not place all n-back pairs")
                    return
                # Pick a random element out of the indices
                ii = idx[random.randint(0,len(idx)-1)]
                # Set pair
                self.sequence[ii] = sym
                self.sequence[ii+self.n] = sym
        # 2. Place the remaining elements
        nRemaining = self.nOccur-2*self.nMatch   # number remaining repetitions
        # Make list with remaining symbols and shuffle it
        remList = []
        for sym in self.symbols:
             remList.extend([sym]*nRemaining)
        random.shuffle(remList)
        for i in range(self.nStim):
            if self.sequence[i] is None:
                self.sequence[i] = remList.pop()
    
    def checkWindowFocus(self):
        """
        Return true if pygame window has focus. Otherwise display text
        and return false.
        """
        pygame.event.get()
        if not pygame.key.get_focused():
            txt = self.font.render("Click to start",self.ANTIALIAS,self.color)
            txt_rect = txt.get_rect(center=self.screenCenter)
            self.screen.blit(self.background,self.background_rect)
            self.screen.blit(txt, txt_rect)
            pygame.display.update()
            return False
        return True
        
        
    
if __name__ == "__main__":
    a = nback_verbal()
    a.on_init()
    a.on_play()

  #  a.on_quit()
   # sys.exit()
