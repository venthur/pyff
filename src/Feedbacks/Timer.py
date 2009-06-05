
import time

from FeedbackBase.Feedback import Feedback

class Timer(Feedback):
    
    def on_init(self):
        self.iterations = 10000
    
    def on_play(self):
        print self.idle_loop(self.iterations)
        
    def idle_loop(self, iterations):
        t1 = time.time()
        for i in range(iterations):
            pass
        t2 = time.time()
        return t2 - t1
        
        
if __name__ == "__main__":
    fb = Timer()
    fb.on_init()
    fb.on_play()
