from Feedback import Feedback

import pygame


class TrivialFeedback(Feedback):

    
    def init(self):
        """Setup the pygame stuff."""
        self.logger.debug("Entered init.")
        
        self.quitting, self.quit = False, False
        self.pause = False
        self.data = [0]
        
        # 30 should be the best all-purpose solution
        # 60 is recommendet for RT-shooters
        self.FPS = 30
        
        
    
    def main_loop(self):
        """Run the main loop."""
        self.logger.debug("Entered main_loop.")
        while 1:
            self.clock.tick(self.FPS)
            # Do nothing on pause
            if self.pause:
                continue
            # Stop the Feedback and leave the mainloop
            if self.quitting:
                break
            
            #
            # The actual main loop
            #
            
            #font = pygame.font.Font(None, 36)
            val = self.data[-1]
            w_half = self.background.get_width() / 2
            pos = w_half + w_half * val

            self.text = self.font.render(str(val), 1, (10, 10, 10))
            #textpos = text.get_rect(centerx=self.background.get_width()/2)
            textpos = self.text.get_rect(centerx=pos)
            
            #self.background.blit(self.text, textpos)
            
            # Draw everything
            self.screen.blit(self.background, (0, 0)) # Erase the old frame
            self.screen.blit(self.text, textpos)      # Draw the new one
            pygame.display.flip()                     # Update the whole scene


        self.logger.debug("Left main_loop.")
        self.quit = True


### To overwrite: ##############################################################
    def on_init(self):
        """"""
        self.init()

    
    def on_play(self):
        """Start the main feedback routine."""
        self.logger.debug("on_play")

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))

        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render("Foo", 1, (10, 10, 10))
        
        self.quitting, self.quit = False, False
        self.main_loop()

    
    def on_pause(self):
        """Pause the main feedback routine."""
        self.logger.debug("on_pause")
        self.pause = not self.pause


    def on_quit(self):
        """Quit the feedback and cleanup."""
        self.logger.debug("on_quit")
        # Important, otherwise the Feedback will hang
        self.quitting = True
        while not self.quit:
            pass
        pygame.quit()

    
    def on_interaction_event(self, data):
        """"""
        self.logger.warn("on_interaction_event")
        self.logger.info(self.__dict__)


    def on_control_event(self, data):
        """"""
        self.logger.warn("on_control_event")
        self.data = data["data"]
        