from Feedback import Feedback
import pygame, random, sys, math, random, os

#class BucketFeedback(Feedback):
class GoalKeeper(Feedback):

################################################################################
# Derived from Feedback
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def on_init(self):
        """
        Initializes variables etc., but not pygame itself.
        """
        #self.logger.debug("on_init")
        
        self.parameters = {
        #   Name from GUI : (local variablename, default value)
            #'duration_until_hit' : ('durationUntilHit', 1500),
            'duration' : ('durationPerTrial', 3000),
            'trials_per_run' : ('trials', 10),
            'break_every' : ('pauseAfter', 5),
            'duration_break' : ('pauseDuration', 9000),
            'directions' : ('availableDirections', ['left', 'right']),
            'fps' : ('FPS', 60),
            'fullscreen' : ('fullscreen', False),
            'screen_width' : ('screenWidth',  1000),
            'screen_height' : ('screenHeight', 700),
            'countdown_from' : ('countdownFrom', 1),
            'hit_miss_duration' : ('hitMissDuration', 1000),
            'time_until_next_trial' : ('timeUntilNextTrial',500)
        }
        for p in self.parameters.values():
            self.__setattr__(p[0], p[1])
        
        self.showGameOverDuration = 1000
        
        self.alternate = True
        
        # Feedback state booleans
        self.quit, self.quitting = False, False
        self.pause, self.shortPause = False, False
        self.gameover, self.hit, self.miss = False, False, False
        self.countdown, self.firstTickOfTrial = True, True
        self.showsPause, self.showsShortPause = False, False
       
        self.elapsed, self.trialElapsed, self.countdownElapsed = 0,0,0
        self.hitMissElapsed, self.shortPauseElapsed, self.completedTrials = 0,0,0
        self.showsHitMiss = False
        
        self.f = 0
        self.hitMiss = [0,0]
        
        # Colours
        self.backgroundColor = (50, 50, 50)
        self.barColor = (237, 100, 148)#(0,50,50)
        self.ballColor = (0,0,255) #(100, 149, 237)
        self.hitFontColor = (0,200,0) 
        self.missFontColor = (200,0,0)
        self.fontColor = (0,150,150)
        self.countdownColor = (237, 100, 148)
        self.frameColor = (165, 171, 172)
        
        # Bowl direction
        self.left = True
        self.down = True
        
        # Classifier threshold for bowl position change
        self.threshold = 0.2
        self.it = 0
        
        
    def on_play(self):
        """
        Initialize pygame, the graphics and start the game.
        """
        #self.logger.debug("on_play")
        self.init_pygame()
        self.init_graphics()
        self.quit = False
        self.quitting = False
        self.main_loop()


    def on_pause(self):
        """
        Flip the pause variable.
        """
        #self.logger.debug("on_pause")
        self.pause = not self.pause
        self.showsPause = False


    def on_quit(self):
        """
        Quit the main loop indirectly by setting quit, wait for the mainloop
        until it has quit and close pygame.
        """
        #self.logger.debug("on_quit")
        self.quitting = True
        #self.logger.debug("Waiting for main loop to quit...")
        while not self.quit:
            pygame.time.wait(100)
        #self.logger.debug("Quitting pygame.")
        pygame.quit()


    def on_interaction_event(self, data):
        """
        Translate the incoming variable-value tuples to the local variables.
        """
        #self.logger.debug("on_interaction_event: %s" % str(data))
        for var, val in data.items():
            if self.parameters.has_key(var):
                local = self.parameters[var][0]
                self.__setattr__(local, val)
            #else:
                #self.logger.warning("Caught unknown variable %s" % str(var))

    def on_control_event(self, data):
        ##self.logger.debug("on_control_event: %s" % str(data))
        self.f = data[-1]

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# Derived from Feedback
################################################################################

    def main_loop(self):
        """
        Main Loop. Represents the loop which refreshes the screen x times per
        second. Runs forever or until the GUI emits the stop signal.
        """
        # just to reset the time when tick was called last time...
        self.clock.tick(self.FPS)
        while not self.quitting:
            self.process_pygame_events()
            pygame.time.wait(10)
            self.elapsed = self.clock.tick(self.FPS)
            self.tick()
        #self.logger.debug("Left the main loop.")
        self.quit = True


    def tick(self):
        """
        One tick of the main loop.
        
        Decides in wich state the feedback currently is and calls the apropriate
        tick method.
        """
        if self.pause:
            self.pause_tick()
        elif self.gameover:
            self.gameover_tick()
        elif self.countdown:
            self.countdown_tick()
        elif self.hit or self.miss:
            self.hit_miss_tick()
        elif self.shortPause:
            self.short_pause_tick()
        else:
            self.trial_tick()
    
    
    def trial_tick(self):
        """
        One tick of the trial loop.
        """
        self.trialElapsed += self.elapsed
        
        if self.firstTickOfTrial:
            # initialize feedback start screen
            self.init_graphics()
            self.draw_initial()
            self.trialElapsed = 0
            self.posX, self.posY = self.ballRect.centerx, self.ballRect.bottom
            pygame.time.wait(self.timeUntilNextTrial)
            self.firstTickOfTrial = False
            self.bowl_pos = 0;  # initially, the bowl is in the middle
            # randomly assign the movement direction of the ball (left(-1) or right(1))
            self.direction = 0;
            while self.direction == 0:
                self.direction = random.randint(-1,1)
            # calculate stepsize dependend on the y-direction
            self.stepY = 1.0 * (self.bowlHeight-self.ballRect.bottom) / ((self.durationPerTrial/1000.0)*self.FPS)
            self.tangens = 1.1 * (self.posX-self.bowl_centers[0][0]) / (self.bowlHeight-self.ballRect.bottom)
            
        self.screen.blit(self.background, self.backgroundRect)    
        
        # Calculate motion of bowl
        self.stepX = self.tangens * self.stepY * self.direction
        
        # Change bowl position according to classifier output (TODO: use self.f)
        ##### only for testing purposes...
        class_out_list = [-1, 0, 1]
        self.it += 1    # TODO: remove self.it after testing (in on_init)
        class_out = math.sin(self.it/30.0)
        ##### end
        self.bowl_pos_before = self.bowl_pos
        self.bowl_pos = int(int(abs(class_out)+self.threshold) * (class_out/abs(class_out)))
        self.bowlRect = self.bowl.get_rect(midbottom=self.bowl_centers[self.bowl_pos+1], size=self.bowlSize)
        self.screen.blit(self.bowl, self.bowlRect) 
             
        # Adapt powerbar according to classifier output 
        (barWidth, barHeight) = self.barSize      
        if class_out>0:
            self.barAreaRect = pygame.Rect(barWidth/2, 0, class_out*barWidth/2, barHeight)
            self.barRect = pygame.Rect(self.barCenter[0], self.barCenter[1]-barHeight/2, class_out*barWidth/2, barHeight)
        elif class_out<0:
            self.barAreaRect = pygame.Rect((1+class_out)*barWidth/2, 0, -class_out*barWidth/2, barHeight)
            self.barRect = pygame.Rect(self.barCenter[0]+class_out*barWidth/2, self.barCenter[1]-barHeight/2, -class_out*barWidth/2, barHeight)
        self.screen.blit(self.bar, self.barRect, self.barAreaRect)
        self.screen.blit(self.frame, self.frameRect)
        self.screen.blit(self.tb1, self.tb1Rect)
        self.screen.blit(self.tb2, self.tb2Rect)
        
        # if bowl is hitting the bowl "surface" 
        if self.ballRect.midbottom[1]+self.stepY >= self.bowlHeight-int(0.4*self.bowlSize[1]): 
            self.ballRect = self.ball.get_rect(midbottom=(self.posX, self.bowlHeight-int(0.4*self.bowlSize[1])))
            # check if bowl is at the same spot 
            # if yes --> hit, else --> miss
            if self.bowl_pos == self.direction: 
                self.hit = True; return
            else:
                self.miss = True; return
        
        # Calculate the new ball position ...
        self.posX = self.posX+self.stepX     
        self.posY = self.posY+self.stepY
        # ... and draw it there
        self.ballRect = self.ball.get_rect(midbottom=(self.posX, self.posY))
        self.screen.blit(self.ball, self.ballRect)
                
        # Repaint everything
        pygame.display.update()


    def pause_tick(self):
        """
        One tick of the pause loop.
        """
        if self.showsPause:
            return
        self.do_print("Pause", self.fontColor, self.size/6)
        self.showsPause = True

        
    def short_pause_tick(self):
        """
        One tick of the short pause loop.
        """
        self.shortPauseElapsed += self.elapsed
        if self.shortPauseElapsed >= self.pauseDuration:
            self.showsShortPause = False
            self.shortPause = False
            self.shortPauseElapsed = 0
            self.countdown = True
            return
        if self.showsShortPause:
            return
        self.do_print("Short Break...", self.fontColor, self.size/6)
        self.showsShortPause = True

    
    def countdown_tick(self):
        """
        One tick of the countdown loop.
        """
        self.countdownElapsed += self.elapsed
        if self.countdownElapsed >= self.countdownFrom * 1000:
            self.countdown = False
            self.countdownElapsed = 0
            return
        t = (self.countdownFrom * 1000 - self.countdownElapsed) / 1000
        self.do_print(str(t), self.countdownColor, self.size/3)

        
    def gameover_tick(self):
        """
        One tick of the game over loop.
        """
        self.do_print("Game Over! (%i : %i)" % (self.hitMiss[0], self.hitMiss[1]), self.fontColor, self.size/6)
        pygame.time.wait(self.showGameOverDuration)

        
    def hit_miss_tick(self):
        """
        One tick of the Hit/Miss loop.
        """
        self.hitMissElapsed += self.elapsed
        if self.hitMissElapsed >= self.hitMissDuration:
            self.hitMissElapsed = 0
            self.hit, self.miss = False, False
            self.showsHitMiss = False
            return
        if self.showsHitMiss:
            return
        
        self.completedTrials += 1; 
        self.firstTickOfTrial = True
        s = ""
        if self.hit:
            s = "Hit"
            color = self.hitFontColor
            self.hitMiss[0] += 1
            
        else:
            s = "Miss"
            color = self.missFontColor
            self.hitMiss[-1] += 1
            
        if self.completedTrials % self.pauseAfter == 0:
            self.shortPause = True
        if self.completedTrials >= self.trials:
            self.gameover = True
            
        self.do_print(s, color, self.size/7)
        self.screen.blit(self.bowl, self.bowlRect)
        self.screen.blit(self.bar, self.barRect, self.barAreaRect)
        self.screen.blit(self.frame, self.frameRect)
        self.screen.blit(self.tb1, self.tb1Rect)
        self.screen.blit(self.tb2, self.tb2Rect)
        self.screen.blit(self.ball, self.ballRect)
        pygame.display.flip()
        self.showsHitMiss = True


    def do_print(self, text, color, size=None, center=None, superimpose=False):
        """
        Print the given text in the given color and size on the screen.
        """
        if not color:
            color = self.fontColor
        if not size:
            size = self.size/10
        if not center:
            center = self.screen.get_rect().center

        font = pygame.font.Font(None, size)
        if not superimpose:
            self.screen.blit(self.background, self.backgroundRect)
        surface = font.render(text, 1, color)
        self.screen.blit(surface, surface.get_rect(center=center))
        if not superimpose:
            pygame.display.update()


    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """
        self.screen = pygame.display.get_surface()
        self.size = min(self.screen.get_height(), self.screen.get_width())
        barWidth = int(self.screenWidth * 0.7)
        barHeight = int(self.screenHeight * 0.1)
        
        path = os.path.dirname( globals()["__file__"] ) 
                
        # init powerbar
        self.barSize = (barWidth, barHeight)
        self.barCenter = (self.screenWidth/2, int(self.screenHeight*(6.0/7)))
        img = pygame.image.load(os.path.join(path, 'powerbar.png')).convert()
        self.bar = pygame.Surface(self.barSize)
        self.bar = pygame.transform.scale(img, self.barSize)
        self.barRect = self.bar.get_rect(center=self.barCenter, size=self.barSize)
        
        # init powerbar frame
        self.frameSize = (int(1.05*barWidth), int(1.3*barHeight))
        img = pygame.image.load(os.path.join(path, 'frame_blue_grad.bmp')).convert()
        self.frame = pygame.Surface(self.frameSize)
        self.frame = pygame.transform.scale(img, self.frameSize)
        self.frame.set_colorkey((255,255,255))
        self.frameRect = self.frame.get_rect(center=self.barCenter, size=self.frameSize)        
        
        # init threshold bars (left and right)
        self.tbSize = (self.frameSize[0]/100, self.frameSize[1])
        self.tb1 = pygame.Surface(self.tbSize)
        self.tb2 = pygame.Surface(self.tbSize)
        c = (16,174,188)
        c = (44,255,255)
        self.tb1.fill(c)
        self.tb2.fill(c)
        self.tb1Rect = self.tb1.get_rect(center=(self.barCenter[0]-(1-self.threshold)*barWidth/2, self.barCenter[1]))
        self.tb2Rect = self.tb2.get_rect(center=(self.barCenter[0]+(1-self.threshold)*barWidth/2, self.barCenter[1]))
        
        # init background
        self.background = pygame.Surface((self.screenWidth, self.screenHeight))
        self.background = self.background.convert()
        self.backgroundRect = self.background.get_rect(center=self.screen.get_rect().center)
        self.background.fill(self.backgroundColor)
        
        # init bowl
        self.bowl = [0]*3
        self.bowlRect = [0]*3
        self.bowlSize = (self.screenWidth/5, self.screenWidth/10)
        gap = (self.screenWidth-3*self.bowlSize[0]) / 4
        self.rotation = [-30, 0, 30]
        self.bowl_centers = []
        self.bowlHeight = int((5.0/7)* self.screenHeight)
        for n in range(3):
            self.bowl_centers.append((gap*(n+1)+int((0.5+n)*self.bowlSize[0]), self.bowlHeight))
        self.bowl = pygame.image.load(os.path.join(path, 'bowls_smaller.bmp')).convert_alpha()
        self.bowl = pygame.transform.rotate(self.bowl, self.rotation[1])
        self.bowlRect = self.bowl.get_rect(midbottom=self.bowl_centers[1], size=self.bowlSize)
        
        # init ball        
        diameter = self.bowlSize[0]/3
        ballSize = (diameter, diameter)
        self.ball = pygame.Surface(ballSize)
        self.ballRect = self.ball.get_rect(center=(self.screenWidth/2, int(0.1 * self.screenHeight)), size=(self.ball.get_width(), self.ball.get_height()))
        self.ball.fill(self.backgroundColor)
        self.ball.set_colorkey(self.backgroundColor)
        pygame.draw.circle(self.ball, self.ballColor, (self.ballRect.width/2,self.ballRect.width/2), diameter/2) 
        

    def draw_initial(self):
        # draw images on the screen
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.bowl, self.bowlRect)
        self.screen.blit(self.frame, self.frameRect)
        self.screen.blit(self.tb1, self.tb1Rect)
        self.screen.blit(self.tb2, self.tb2Rect)
        self.screen.blit(self.ball, self.ballRect)
        pygame.display.flip()


    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        pygame.init()
        pygame.display.set_caption('GoalKeeper')
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screenWidth, self.screenHeight), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()


    def process_pygame_events(self):
        """
        Process the the pygame event queue and react on VIDEORESIZE.
        """
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.init_graphics()
            elif event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                sys.exit()

# HACK
    def main(self):
        self.on_init()
        self.on_play()


if __name__ == '__main__':
    GoalKeeper().main()
