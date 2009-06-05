from processing import Process, Pipe
import logging

from lib.PluginController import PluginController

class FeedbackProcessController(object):
    """Takes care of starting and stopping of Feedback Processes."""
    
    def __init__(self, plugindirs, baseclass, timeout):
        '''
        Initializes the Feedback Process Controller.
        
        @param plugindirs:
        @param baseclass:
        @param timeout:
        '''
        self.logger = logging.getLogger("FeedbackProcessController")
        self.currentProc = None
        self.timeout = timeout
        self.pluginController = PluginController(plugindirs, baseclass)
        self.pluginController.find_plugins()
        
    
    def start_feedback(self, name):
        """Starts the given Feedback in a new process."""
        self.logger.debug("Starting new Process...",)
        self.currentProc = Process(target=self.__start_feedback, args=(name,))
        self.currentProc.start()
        self.logger.debug("done.")

    
    def __start_feedback(self, name):
        try:
            feedbackClass = self.pluginController.load_plugin(name)
        except ImportError:
            # TODO: Hmm anything else we can do?
            raise
        feedback = feedbackClass()
    
    
    def stop_feedback(self):
        """Stops the current Process.
        
        First it tries to join the process with the given timeout, if that fails
        it terminates the process the hard way.
        """
        self.logger.debug("Stopping process...",)
        self.currentProc.join(self.timeout)
        if self.currentProc.isAlive():
            self.logger.debug("process still alive, killing it...",)
            self.currentProc.terminate()
        self.logger.debug("done.")
        
    
    def is_alive(self):
        """Return whether the current Process is alive or not."""
        return self.currentProc.isAlive() if self.currentProc else False
    
    def get_feedbacks(self):
        """Returns a list of available Feedbacks."""
        return self.pluginController.availablePlugins.keys()
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    from FeedbackBase.Feedback import Feedback
    fpc = FeedbackProcessController(["../Feedbacks"], Feedback, 1)
    print fpc.get_feedbacks()
    print "Is alive: ", fpc.is_alive()
    fpc.start_feedback(fpc.get_feedbacks()[1])
    print "Is alive: ", fpc.is_alive()
    fpc.stop_feedback()
    print "Is alive: ", fpc.is_alive()
    
    