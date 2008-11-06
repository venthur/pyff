# Lesson04 - Reacting on control- and interaction events

from FeedbackBase.Feedback import Feedback

class Lesson04(Feedback):
    
    def on_init(self):
        self.myVariable = None
        self.eegTuple = None
    
    def on_interaction_event(self, data):
        # this one is equivalent to:
        # self.myVariable = self._someVariable
        self.myVariable = data.get("someVariable")
        print self.myVariable
        
    def on_control_event(self, data):
        # this one is equivalent to:
        # self.eegTuple = self._data
        self.eegTuple = data
        print self.eegTuple
