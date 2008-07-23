# Lesson06 - Logging

from Feedback import Feedback

class Lesson06(Feedback):
    
    def on_init(self):
        self.logger.debug("Feedback successfully loaded.")
    
    def on_quit(self):
        self.logger.debug("Feedback quit.")
