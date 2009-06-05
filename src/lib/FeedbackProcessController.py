from processing import Process, Pipe
from threading import Thread, Event
import logging
import traceback

from lib.PluginController import PluginController
from bcixml import BciSignal
import bcixml

def pipe_loop(self):
    while True:
        item = self.conn[0].recv()
        if not isinstance(item, BciSignal):
            # ok got something fishy
            self.logger.warning("Received something which is not a BciSignal, ignoring it.")
            continue
        if item.commands == bcixml.CMD_PLAY:
            self.playEvent.set()
        

class FeedbackProcessController(object):
    """Takes care of starting and stopping of Feedback Processes."""
    
    def __init__(self, plugindirs, baseclass, timeout):
        """
        Initializes the Feedback Process Controller.
        
        @param plugindirs:
        @param baseclass:
        @param timeout:
        """
        self.logger = logging.getLogger("FeedbackProcessController")
        self.currentProc = None
        self.timeout = timeout
        self.pluginController = PluginController(plugindirs, baseclass)
        self.pluginController.find_plugins()
        self.fbPipe = Pipe()
        
    
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
        feedbackClass.pipe_loop = pipe_loop
        feedback = feedbackClass()

        feedback.conn = self.fbPipe
        feedback.playEvent = Event()
        feedback.on_init()
        pipeThread = Thread(target=feedback.pipe_loop)
        pipeThread.start()
        while True:
            feedback.playEvent.wait()
            try:
                feedback.on_play()
            except:
                print "Feedbacks on_play threw an exception:"
                print traceback.format_exc()
            feedback.playEvent.clear()
            print "Feedback's on_play terminated."

    
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
    import time
    fpc = FeedbackProcessController(["../Feedbacks"], Feedback, 1)
    print fpc.get_feedbacks()
    print "Is alive: ", fpc.is_alive()
    fpc.start_feedback(fpc.get_feedbacks()[1])
    print "Is alive: ", fpc.is_alive()
    fpc.fbPipe[1].send("foo")
    fpc.fbPipe[1].send(BciSignal(None, bcixml.CMD_PLAY, bcixml.INTERACTION_SIGNAL))
    time.sleep(10)
    fpc.stop_feedback()
    time.sleep(1)
    print "Is alive: ", fpc.is_alive()
