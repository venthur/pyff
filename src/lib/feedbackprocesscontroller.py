from processing import Process, Pipe
from threading import Thread, Event
import logging
import traceback

from lib.PluginController import PluginController
from bcixml import BciSignal
import bcixml

def pipe_loop(self):
    while True:
        self.conn[0].poll(None)
        item = self.conn[0].recv()
        self.logger.debug("Received via pipe: %s", str(item))
        if not isinstance(item, BciSignal):
            # ok got something fishy
            self.logger.warning("Received something which is not a BciSignal, ignoring it.")
            continue
        _process_signal(item, self)


def _process_signal(signal, feedback):
    cmd = signal.commands[0] if len(signal.commands) > 0 else None
    if cmd == bcixml.CMD_PLAY:
        feedback.playEvent.set()
    elif cmd == bcixml.CMD_PAUSE:
        feedback._on_pause()
    elif cmd == bcixml.CMD_STOP:
        feedback._on_stop()
    elif cmd == bcixml.CMD_QUIT:
        feedback._on_quit()
    elif cmd == bcixml.CMD_SEND_INIT:
        feedback._on_init()

#FeedbackProcessController:
#
#* Get available Feedbacks
#* Start a Feedback in a new Process
#* Stop Feedback
#* Send data (Signals) to the Feedback
#* Get Data from the Feedback
#* Test if Feedback is alive
#
#How to use:
#
#1. instantiate FPC
#2. get_feedbacks
#3. start_feedback(name)
#  - send and get various data
#4. stop_feedback

#class FeedbackProcessController(object):
#    
#    def __init__(self, plugindirs, baseclass, timeout): pass
#    def get_feedbacks(self): pass
#    def start_feedback(self, name): pass
#    def stop_feedback(self): pass
#    def send_signal(self, signal): pass


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
                print """Trying to start Feedback's on_play...""",
                feedback.on_play()
                print """done."""
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
    
    def send_signal(self, signal):
        """Send the signal to the Feedback process."""
        self.fbPipe[1].send(signal)
        
    def poll(self):
        """Return if there is something to read from the Feedback process."""
        return self.fbPipe[1].poll()
    
    def receive_signal(self):
        """Read from the Feedback process."""
        return self.fbPipe[1].recv()

    
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
