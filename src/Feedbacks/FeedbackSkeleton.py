
from Feedback import Feedback
import time

class FeedbackSkeleton(Feedback):
    
################################################################################
# From Feedback Base Class
################################################################################
    def on_init(self):
        self.stopping, self.stopped, self.paused = False, False, False
    
    def on_play(self):
        self.main_loop()
    
    def on_pause(self):
        self.paused = not self.paused

    def on_quit(self):
        self.stopping = True
        while not self.stopped:
            pass
    
    def on_interaction_event(self, data):
        pass

    def on_control_event(self, data):
        pass
################################################################################
# /From Feedback Base Class
################################################################################

    def main_loop(self):
        while not self.stopping:
            time.sleep(1)
            if self.paused:
                self.logger.debug("Pause.")
                continue
            elif self.stopping:
                self.logger.debug("Stopping.")
                break
            #
            # Here goes the actual main loop code
            #
            self.logger.debug("Main-Looping.")
        self.stopped = True
    

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    fb = FeedbackSkeleton()
    fb.on_init()
    fb.on_play()
