# Lesson01 - Sending Markers

from FeedbackBase.Feedback import Feedback

class Lesson05(Feedback):
    
    def on_init(self):
        self.send_parallel(0x1)
    
    def on_play(self):
        self.send_parallel(0x2)
    
    def on_pause(self):
        self.send_parallel(0x4)
    
    def on_quit(self):
        self.send_parallel(0x8)
