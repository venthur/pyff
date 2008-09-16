# Lesson03 - Working with data send by control- and interaction signals

from Feedback import Feedback

import time

class Lesson03(Feedback):
    
    def on_init(self):
        print "Feedback successfully loaded."
        self.quitting, self.quit = False, False
        self.pause = False
    
    def on_quit(self):
        self.quitting = True
        # Make sure we don't return on_quit until the main_loop (which runs in
        # a different thread!) quit.
        print "Waiting for main loop to quit."
        while not self.quit:
            pass
        # Now the main loop quit and we can safely return

    def on_play(self):
        # Start the main loop. Note that on_play runs in a different thread than
        # all the other Feedback methods, and so does the main loop.
        self.quitting, self.quit = False, False
        self.main_loop()
        
    def on_pause(self):
        self.pause = not self.pause
        
    def main_loop(self):
        i = 0
        while 1:
            time.sleep(0.5)
            if self.pause:
                print "Feedback Paused."
                continue
            elif self.quitting:
                print "Leaving main loop."
                break
            print self._data
            
        print "Left main loop."
        self.quit = True