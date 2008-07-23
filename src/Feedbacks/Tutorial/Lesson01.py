# Lesson01 - Trivial Feedback without functionality

from Feedback import Feedback

class Lesson01(Feedback):
    
    def on_init(self):
        print "Feedback successfully loaded."
    
    def on_quit(self):
        print "Feedback quit."
