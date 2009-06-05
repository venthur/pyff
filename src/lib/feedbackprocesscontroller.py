from processing import Process, Pipe
from threading import Thread, Event
from pickle import UnpicklingError
import logging
import traceback

from lib.PluginController import PluginController
from bcixml import BciSignal
import bcixml

def pipe_loop(self):
    while True:
        self.conn[0].poll(None)
        try:
            item = self.conn[0].recv()
        except UnpicklingError, e:
            self.logger.error("Unable to unpickle Data:")
            self.logger.error(str(item))
            self.logger.error(str(e))
            self.logger.error(traceback.format_exc())
            continue
        self.logger.debug("Received via pipe: %s", str(item))
        if not isinstance(item, BciSignal):
            self.logger.warning("Received something which is not a BciSignal, ignoring it.")
            continue
        try:
            _process_signal(item, self)
        except:
            self.logger.error("Exception during _process_sigal:")
            self.logger.error(traceback.format_exc())


def _process_signal(signal, feedback):
    if signal.type == bcixml.CONTROL_SIGNAL:
        feedback._on_control_event(signal.data)
        return
    
    cmd = signal.commands[0] if len(signal.commands) > 0 else None
    if cmd == bcixml.CMD_GET_VARIABLES:
        reply = bcixml.BciSignal({"variables" : feedback._get_variables()}, None,
                                 bcixml.REPLY_SIGNAL)
        reply.peeraddr = signal.peeraddr
        feedback.conn[0].send(reply)
    elif cmd == bcixml.CMD_PLAY:
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
        self.fbPipe = None
        self.timeout = timeout
        self.pluginController = PluginController(plugindirs, baseclass)
        self.pluginController.find_plugins()
        
    
    def start_feedback(self, name):
        """Starts the given Feedback in a new process."""
        self.logger.debug("Starting new Process...",)
        if self.currentProc:
            self.logger.warning("Trying to start feedback but another one is still running. Killing the old one now and proceed.")
            self.stop_feedback()
        self.fbPipe = Pipe()
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
        # TODO: Do we need to kill the thread?
        pipeThread = Thread(target=feedback.pipe_loop)
        pipeThread.start()
        while True:
            feedback.playEvent.wait()
            try:
                self.logger.debug("Trying to start Feedback's on_play...",)
                feedback.on_play()
                self.logger.debug("done.")
            except:
                self.logger.error("Feedbacks on_play threw an exception:")
                self.logger.error(traceback.format_exc())
            feedback.playEvent.clear()
            self.logger.debug("Feedback's on_play terminated.")

    
    def stop_feedback(self):
        """Stops the current Process.
        
        First it tries to join the process with the given timeout, if that fails
        it terminates the process the hard way.
        """
        self.logger.debug("Stopping process...",)
        if not self.currentProc:
            self.logger.debug("No process running, nothing to do.")
            return
        self.currentProc.join(self.timeout)
        if self.currentProc.isAlive():
            self.logger.debug("process still alive, killing it...",)
            self.currentProc.terminate()
            # The above does not always work... maybe os.kill does?
        self.fbPipe[0].close()
        self.fbPipe[1].close()
        del(self.currentProc)
        self.currentProc = None
        self.logger.debug("done.")
        
    
    def is_alive(self):
        """Return whether the current Process is alive or not."""
        return self.currentProc.isAlive() if self.currentProc else False

    
    def get_feedbacks(self):
        """Returns a list of available Feedbacks."""
        return self.pluginController.availablePlugins.keys()
    
    def send_signal(self, signal):
        """Send the signal to the Feedback process."""
        if not self.currentProc:
            return
        self.fbPipe[1].send(signal)
        
    def poll(self):
        """Return if there is something to read from the Feedback process."""
        if not self.currentProc:
            return
        return self.fbPipe[1].poll()
    
    def receive_signal(self):
        """Read from the Feedback process."""
        if not self.currentProc:
            return
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
