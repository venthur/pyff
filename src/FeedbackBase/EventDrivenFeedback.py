
from FeedbackBase.Feedback import Feedback

class EventDrivenFeedback(Feedback):

    def __init__(self):
        self.event_method_mapping = dict()
        self.enabled_events = list()
        # in seconds
        self.remaining_time = 0.0

    def execute(self, eventlist, time):
        """Bind the given event to their assigned events and execute them for
        the given time.
        """
        self.enabled_events = eventlist
        self.remaining_time = time



    def dispatch_event(self, event):
        """Dispatch the event and run the associated method if enabled."""
        if self.is_enabled(event):
            # Call the event method
            self.event_method_method(event)()


    def bind_event_to_method(self, event, method):
        """Bind event to methodcall."""
        self.event_method_binding[event] = method



if __name__ == "__main__":
    fb = EventDrivenFeedback()
    fb.bind_event_to_method(
