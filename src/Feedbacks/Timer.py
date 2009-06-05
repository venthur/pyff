
import time

from FeedbackBase.Feedback import Feedback

class Timer(Feedback):
    
    def on_init(self):
        self.iterations = 100000000
    
    def on_play(self):
        t1 = time.time()
        for i in xrange(self.iterations):
            pass
        t2 = time.time()
        print t2 - t1
        
        
if __name__ == "__main__":
    fb = Timer()
    fb.on_init()
    fb.on_play()
