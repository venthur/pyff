
import os

import pygame

from MainloopFeedback import MainloopFeedback


class PygameFeedback(MainloopFeedback):

    def init(self):
        self.FPS = 30
        self.screenPos = [0, 0]
        self.screenSize = [800, 600]
        self.fullscreen = False
        self.caption = "PygameFeedback"
        self.elapsed = 0
        self.backgroundColor = [0, 0, 0]
        # For keys
        self.keypressed = False
        self.lastkey = None


    def pre_mainloop(self):
        self.init_pygame()
        self.init_graphics()


    def post_mainloop(self):
        self.quit_pygame()


    def tick(self):
        self.process_pygame_events()
        self.elapsed = self.clock.tick(self.FPS)


    def pause_tick(self):
        pass


    def play_tick(self):
        pass


    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.screenPos[0],
                                                        self.screenPos[1])
        pygame.init()
        pygame.display.set_caption(self.caption)
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.screenSize[0],
                                                   self.screenSize[1]),
                                                   pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.screenSize[0],
                                                   self.screenSize[1]),
                                                   pygame.RESIZABLE)
        self.clock = pygame.time.Clock()


    def quit_pygame(self):
        pygame.quit()


    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """
        pass


    def process_pygame_events(self):
        """
        Process the the pygame event queue and react on VIDEORESIZE.
        """
        for event in pygame.event.get():
            self.process_pygame_event(event)

            
    def process_pygame_event(self, event):
        """Process a signle pygame event."""
        if event.type == pygame.VIDEORESIZE:
            e = max(event.w, int(round(event.h * 0.9)))
            self.screen = pygame.display.set_mode((e, event.h), pygame.RESIZABLE)
            self.resized = True
            self.screenSize = [self.screen.get_height(), self.screen.get_width()]
            self.init_graphics()
        elif event.type == pygame.QUIT:
            self.on_stop()
        elif event.type == pygame.KEYDOWN:
            self.keypressed = True
            self.lastkey = event.key
            self.lastkey_unicode = event.unicode
                
    
    def wait_for_pygame_event(self):
        """Wait until a pygame event orcurs and process it."""
        event = pygame.event.wait()
        self.process_pygame_event(event)
