# Lesson01b - Trivial Feedback without functionality - alternative with __init__
#   overwritten

from Feedback import Feedback

class Lesson01b(Feedback):
    
    def __init__(self, pp):
        Feedback.__init__(self, pp, "foo-")
        # Your own stuff goes here
    
    def on_init(self):
        print "Feedback successfully loaded."
    
    def on_quit(self):
        print "Feedback quit."
