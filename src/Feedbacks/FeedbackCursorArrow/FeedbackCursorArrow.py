from Feedback import Feedback
import pygame
import random

class FeedbackCursorArrow(Feedback):

################################################################################
# Derived from Feedback
#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

    def on_init(self):
        """
        Initializes the variables and stuff, but not pygame itself.
        """
        # TODO: move variables to parameters, check for unused variables
        self.logger.debug("on_init")
        
        self.parameters = {
        #   Name from GUI : (local variablename, default value)
            'duration_until_hit' : ('durationUntilHit', 1500),
            'duration' : ('durationPerTrial', 4000),
            'trials_per_run' : ('trials', 10),
            'break_every' : ('pauseAfter', 5),
            'duration_break' : ('pauseDuration', 9000),
            'directions' : ('availableDirections', ['left', 'right']),
            'fps' : ('FPS', 30),
            'fullscreen' : ('fullscreen', False),
            'screen_width' : ('screenWidht',  600),
            'screen_height' : ('screenHeight', 600),
            'countdown_from' : ('countdownFrom', 4),
            'hit_miss_duration' : ('hitMissDuration', 1000)
        }
        for p in self.parameters.values():
            self.__setattr__(p[0], p[1])
        
        self.pause = False
        self.quit = False
        self.quitting = False
        
        self.gameover = False
        self.countdown = True
        self.hit = False
        self.miss = False
        self.shortPause = False
        
        self.firstTickOfTrial = True
        
        self.showsPause, self.showsShortPause, self.showsHitMiss, self.showsGameover = False, False, False, False
        
        self.elapsed = 0
        self.trialElapsed = 0
        self.countdownElapsed = 0
        self.hitMissElapsed = 0
        self.shortPauseElapsed = 0
        
        self.completedTrials = 0
        
        self.f = 0
        self.hitMiss = [0,0]
        
        self.arrowPointlist = [(.5,0), (.5,.33), (1,.33), (1,.66), (.5,.66), (.5,1), (0,.5)]
        self.arrowColor = (127, 127, 127)
        self.borderColor = self.arrowColor
        self.backgroundColor = (64, 64, 64)
        self.cursorColor = (100, 149, 237)
        self.fontColor = self.cursorColor
        self.countdownColor = (237, 100, 148)
        
        self.borderWidth = 20
        
        # How many degrees counter clockwise to turn an arrow pointing to the 
        # left to point at left, right and foot
        self.LEFT, self.RIGHT, self.DOWN, self.UP = 'left', 'right', 'foot', 'up'
        self.directions = {self.LEFT: 0, self.RIGHT: 180, self.DOWN: 90, self.UP: 270}
        self.availableDirections = [None, None]


    def on_play(self):
        """
        Initialize pygame, the graphics and start the game.
        """
        self.logger.debug("on_play")
        self.init_pygame()
        self.init_graphics()
        self.quit = False
        self.quitting = False
        self.main_loop()
        pygame.quit()


    def on_pause(self):
        """
        Flip the pause variable.
        """
        self.logger.debug("on_pause")
        self.pause = not self.pause
        self.showsPause = False


    def on_quit(self):
        """
        Quit the main loop indirectly by setting quit, wait for the mainloop
        until it has quit and close pygame.
        """
        self.logger.debug("on_quit")
        self.quitting = True
        self.logger.debug("Waiting for main loop to quit...")
        while not self.quit:
            pygame.time.wait(100)
        self.logger.debug("Quitting pygame.")
        pygame.quit()


    def on_interaction_event(self, data):
        """
        Translate the incoming variable-value tuples to the local variables.
        """
        self.logger.debug("on_interaction_event: %s" % str(data))
        for var, val in data.items():
            if self.parameters.has_key(var):
                local = self.parameters[var][0]
                self.__setattr__(local, val)
            else:
                self.logger.warning("Caught unknown variable %s" % str(var))


    def on_control_event(self, data):
        #self.logger.debug("on_control_event: %s" % str(data))
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
        self.logger.debug("Left the main loop.")
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

        # Teste ob erster Tick im Trial
        if self.firstTickOfTrial:
            self.firstTickOfTrial = False
            self.trialElapsed = 0
            self.pos = 0
        
            self.targetDirection = random.randint(0,1)
            self.myarrow = pygame.transform.rotate(self.arrow, self.directions[self.availableDirections[self.targetDirection]])
            self.myarrowRect = self.myarrow.get_rect(center=self.screen.get_rect().center)
        
        # Teste ob zeit fuer alten Trial abgelaufen ist
        if self.trialElapsed >= self.durationPerTrial:
            self.miss = True
            return
        # sonst laufe im normalen Trial weiter
        # Redraw background and arrow
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.myarrow, self.myarrowRect)
        
        # Calculate motion of cursor, where s is the amount of pixels the 
        # cursor moves
        # Formula: s = f * size/2 / durationUntilHit * t
        #
        # if pos = pos + s for every frame, then
        # pos should *g* be in [-size/2 .. size/2]
        s = self.f * self.size/2 / self.durationUntilHit * self.elapsed
        self.pos += s
        
        if abs(self.pos) >= self.size/2:
            if (self.pos < 0 and self.targetDirection == 0) or (self.pos > 0 and self.targetDirection == 1):
                self.hit = True
                return
            else:
                self.miss = True
                return
        
        # Draw the cursor
        self.cursorRect.center = self.backgroundRect.center
        self.direction = self.availableDirections[0]
        if self.pos > 0:
            self.direction = self.availableDirections[1]
        arrowPos = { self.LEFT  : (-abs(self.pos),0),
                     self.RIGHT : (abs(self.pos),0),
                     self.DOWN  : (0,abs(self.pos)),
                     self.UP    : (0,-abs(self.pos))
                    }[self.direction]
        self.cursorRect.move_ip(arrowPos)
        self.screen.blit(self.cursor, self.cursorRect)

        # Repaint everything
        pygame.display.update()
        
    
    def pause_tick(self):
        """
        One tick of the pause loop.
        """
        if self.showsPause:
            return
        self.do_print("Pause", self.fontColor, self.size/4)
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
        self.do_print("Short Break...", self.fontColor, self.size/4)
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
        # TODO: showsGameover auf False setzen
        if self.showsGameover:
            return
        self.do_print("Game Over! (%i : %i)" % (self.hitMiss[0], self.hitMiss[1]))
        self.showsGameover = True

        
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
        
        self.completedTrials += 1
        self.firstTickOfTrial = True
        s = ""
        if self.hit:
            s = "Hit"
            self.hitMiss[0] += 1
        else:
            s = "Miss"
            self.hitMiss[-1] += 1

        if self.completedTrials % self.pauseAfter == 0:
            self.shortPause = True
        if self.completedTrials >= self.trials:
            self.gameover = True
            
        self.do_print(s)
        self.showsHitMiss = True
    
    
    def do_print(self, text, color=None, size=None):
        """
        Print the given text in the given color and size on the screen.
        """
        if not color:
            color = self.fontColor
        if not size:
            size = self.size/10

        font = pygame.font.Font(None, size)
        self.screen.blit(self.background, self.backgroundRect)
        surface = font.render(text, 1, color)
        self.screen.blit(surface, surface.get_rect(center=self.screen.get_rect().center))
        pygame.display.update()


    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """
        self.screen = pygame.display.get_surface()
        self.size = min(self.screen.get_height(), self.screen.get_width())
    
        scale = self.size / 3
        scaledArrow = [(P[0]*scale, P[1]*scale) for P in self.arrowPointlist]
        self.arrow = pygame.Surface((scale, scale))
        self.arrowRect = self.arrow.get_rect(center=self.screen.get_rect().center)
        self.arrow.fill(self.backgroundColor)
        pygame.draw.polygon(self.arrow, self.arrowColor, scaledArrow)
    
        scale = self.size / 5
        self.cursor = pygame.Surface((scale, scale))
        self.cursorRect = self.cursor.get_rect(center=self.screen.get_rect().center)
        self.cursor.set_colorkey((0,0,0))
        pygame.draw.line(self.cursor, self.cursorColor, (0,scale/2),(scale,scale/2), 10)
        pygame.draw.line(self.cursor, self.cursorColor, (scale/2,0),(scale/2,scale), 10)
    
        self.background = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        self.backgroundRect = self.background.get_rect(center=self.screen.get_rect().center)
        self.background.fill((0,0,0))
        rect = pygame.Rect(self.screen.get_rect().center, (self.size, self.size))
        rect.center = self.screen.get_rect().center
        pygame.draw.rect(self.background, self.backgroundColor, rect, 0)
        pygame.draw.rect(self.background, self.borderColor, rect, self.borderWidth)
    
        self.screen.blit(self.background, self.backgroundRect)
        self.screen.blit(self.arrow, self.arrowRect)
        self.screen.blit(self.cursor, self.cursorRect)
        
        pygame.display.update()


    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        pygame.init()
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screenWidht, self.screenHeight), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screenWidht, self.screenHeight), pygame.RESIZABLE)
        self.w = self.screen.get_width()
        self.h = self.screen.get_height()
        self.clock = pygame.time.Clock()


    def process_pygame_events(self):
        """
        Process the the pygame event queue and react on VIDEORESIZE.
        """
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.init_graphics()
