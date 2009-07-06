# feedbackprocesscontroller.py -
# Copyright (C) 2009  Bastian Venthur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import sys
from threading import Thread, Event
from pickle import UnpicklingError
import logging
import traceback

from processing import Process, Pipe

from lib.PluginController import PluginController
from bcixml import BciSignal
import bcixml


def pipe_loop(self):
    # Where are we: 
    # Proc/Thread: FC/IO
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
            sys.exit(1)


def _process_signal(signal, feedback):
    # Where are we: 
    # Proc/Thread: FB/IO
    feedback.logger.debug("Processing signal")
    
    if signal.type == bcixml.CONTROL_SIGNAL:
        feedback._on_control_event(signal.data)
        return
    
    cmd = signal.commands[0] if len(signal.commands) > 0 else None
    if cmd == bcixml.CMD_GET_VARIABLES:
        reply = bcixml.BciSignal({"variables" : feedback._get_variables()}, None,
                                 bcixml.REPLY_SIGNAL)
        reply.peeraddr = signal.peeraddr
        feedback.logger.debug("Sending variables")
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


def start_feedback_proc_wrapper(feedbackClass, fbPipe):
    # Where are we: 
    # Proc/Thread: FB/Main
    logger = logging.getLogger("start_fb_proc_wrapper")
    feedbackClass.pipe_loop = pipe_loop
    # FIXME dammnit
    feedback = feedbackClass()

    feedback.conn = fbPipe
    feedback.playEvent = Event()
    feedback.on_init()
    # TODO: Do we need to kill the thread?
    pipeThread = Thread(target=feedback.pipe_loop)
    pipeThread.start()
    while True:
        feedback.playEvent.wait()
        try:
            logger.debug("Trying to start Feedback's on_play...",)
            feedback.on_play()
            logger.debug("done.")
        except:
            # The feedback's main thread crashed and we need to take care
            # that the pipe does not run full, otherwise the feedback
            # controller freezes on the last pipe[foo].send()
            # So let's just terminate the feedback process.
            logger.error("Feedbacks on_play threw an exception:")
            logger.error(traceback.format_exc())
            return
        feedback.playEvent.clear()
        logger.debug("Feedback's on_play terminated.")


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

# TODO: If the pipe overrunns, then the last send() becomes blocking -- this means the FC will freeze if the pipe is not cleared regularily

class FeedbackProcessController(object):
    """Takes care of starting and stopping of Feedback Processes."""
    
    def __init__(self, plugindirs, baseclass, timeout):
        """
        Initializes the Feedback Process Controller.
        
        @param plugindirs:
        @param baseclass:
        @param timeout:
        """
        # Where are we: 
        # Proc/Thread: FB/??
        self.logger = logging.getLogger("FeedbackProcessController")
        self.currentProc = None
        self.fbPipe = None
        self.timeout = timeout
        self.pluginController = PluginController(plugindirs, baseclass)
        self.pluginController.find_plugins()
        
    
    def start_feedback(self, name):
        """Starts the given Feedback in a new process."""
        # Where are we: 
        # Proc/Thread: FC/??
        self.logger.debug("Starting new Process...",)
        if self.currentProc:
            self.logger.warning("Trying to start feedback but another one is still running. Killing the old one now and proceed.")
            self.stop_feedback()
        self.fbPipe = Pipe()
        try:
            feedbackClass = self.pluginController.load_plugin(name)
        except ImportError:
            # TODO: Hmm anything else we can do?
            raise
        self.currentProc = Process(target=start_feedback_proc_wrapper, args=(feedbackClass, self.fbPipe))
        self.currentProc.start()
        self.logger.debug("done.")

    
    def stop_feedback(self):

        """Stops the current Process.
        
        First it tries to join the process with the given timeout, if that fails
        it terminates the process the hard way.
        """
        # Where are we: 
        # Proc/Thread: FC/??
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
        # Where are we: 
        # Proc/Thread: FC/??
        if not self.currentProc:
            return False
        return self.currentProc.isAlive() if self.currentProc else False

    
    def get_feedbacks(self):
        """Returns a list of available Feedbacks."""
        # Where are we: 
        # Proc/Thread: FC/??
        return self.pluginController.availablePlugins.keys()
    
    def send_signal(self, signal):
        """Send the signal to the Feedback process."""
        # Where are we: 
        # Proc/Thread: FC/??
        if not self.is_alive():
            return
        self.fbPipe[1].send(signal)
        
    def poll(self):
        """Return if there is something to read from the Feedback process."""
        # Where are we: 
        # Proc/Thread: FC/??
        if not self.is_alive():
            return
        return self.fbPipe[1].poll()
    
    def receive_signal(self):
        """Read from the Feedback process."""
        # Where are we: 
        # Proc/Thread: FC/??
        if not self.is_alive():
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
