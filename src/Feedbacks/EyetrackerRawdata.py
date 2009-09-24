# 2009 Matthias Sebastian Treder

from FeedbackBase.MainloopFeedback import MainloopFeedback
from lib.eyetracker import EyeTracker

class EyetrackerRawdata(MainloopFeedback):

    def pre_mainloop(self):
        # Start eye tracker
        self.et = EyeTracker()
        self.et.start()
        
    def play_tick(self):
        print self.et.x, self.et.y, self.et.duration

    def post_mainloop(self):
        # Stop eyetracker
        self.et.stop()
