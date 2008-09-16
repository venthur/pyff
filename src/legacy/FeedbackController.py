#!/usr/bin/env python

# FeedbackController.py -
# Copyright (C) 2007-2008  Bastian Venthur
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

from UdpDecoder import *
from Feedback import Feedback

import parallel

import logging
import socket
import thread
import Queue
import traceback
import sys
from optparse import OptionParser


# Port and Maximum Package Size for the Interaction Signal
IS_PORT = 12470
IS_BUFFER_SIZE = 65535


# Port and Maximum Package Size for the Control Signal
CS_PORT = 12489
CS_BUFFER_SIZE = 65535


class FeedbackController:
    
    def __init__(self):
        """Initializes the logger and the event queue."""
        # Analyze the command line
        parser = OptionParser()
        parser.add_option('-l', '--loglevel', dest='loglevel', default='warning', 
                          help='Set the loglevel for the Feedbacks and the Feedback Controller. Accepted values are: notset, debug, info, warning, error and critical, default loglevel is "warning".')
        # FIXME: not really a fulllog anymore
        parser.add_option('-f', '--file', action='store_true', dest='fulllog', default=False,
                          help='Log everything into a logfile.')
        parser.add_option('--fb-loglevel', dest='fbloglevel', default='warning', 
                          help='Set the loglevel for the Feedbacks. Default is "warning"')
        parser.add_option('--fc-loglevel', dest='fcloglevel', default='warning', 
                          help='Set the loglevel for the Feedback Controller. Default is "warning"')
        options, args = parser.parse_args()

        levels = {'notset': logging.NOTSET, 
                  'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL
                  }
        loglevel = levels.get(options.loglevel, logging.WARNING)
        fbLoglevel = levels.get(options.fbloglevel, logging.WARNING)
        fcLoglevel = levels.get(options.fcloglevel, logging.WARNING)
        
        fbLoglevel = min(fbLoglevel, loglevel)
        fcLoglevel = min(fcLoglevel, loglevel)
        
        # Setup the Logger
        logging.getLogger('').setLevel(logging.NOTSET)
        # Set the console output...
        console = logging.StreamHandler()
        console.setLevel(logging.NOTSET)
        consoleFormatter = logging.Formatter('[%(threadName)-10s] %(name)-20s: %(levelname)-8s %(message)s')
        console.setFormatter(consoleFormatter)
        logging.getLogger('').addHandler(console)
        # ... the file output if desired
        # FIXME: Should fulllog overwrite the levels of fc and fb?
        if options.fulllog:
            file = logging.FileHandler('logfile.txt', 'w')
            file.setLevel(logging.NOTSET)
            fileFormatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
            file.setFormatter(fileFormatter)
            logging.getLogger('').addHandler(file)
        # ... the loglevel for the Feedback Controller and it's childs
        self.logger = logging.getLogger('FC')
        self.logger.setLevel(fcLoglevel)
        self.logger.debug("Loaded my logger.")
        # ... the loglevel for the Feedback
        logging.getLogger('Feedback').setLevel(fbLoglevel)
        # TODO: convert all logging.foo to self.logger.foo
        
        self.decoder = UdpDecoder()
        
        # Setup the event queue
        self.q = Queue.Queue()
        
        # Setup the parallel port
        self.pp = None
        try:
            self.pp = parallel.Parallel()
        except:
            self.logger.error("Unable to open parallel port!")
        
        self.feedback = Feedback(self.pp)

    def __del__(self):
        self.logger.info("Quitting the Feedback Controller.")
        logging.shutdown()

    def handle_event(self, e):
        if e.type == Event.CONTROL_EVENT:
            self.logger.info("Received control signal")
            self.feedback._Feedback__on_control_event(e.data)
        elif e.type == Event.INTERACTION_EVENT:
            # Check the subtype if available
            self.feedback._Feedback__on_interaction_event(e.data)
            if e.subtype == Event.PLAY:
                self.logger.info("Received PLAY signal")
                self.feedback._Feedback__on_play()
            elif e.subtype == Event.PAUSE:
                self.logger.info("Received PAUSE signal")
                self.feedback._Feedback__on_pause()
            elif e.subtype == Event.QUIT:
                self.logger.info("Received QUIT signal")
                self.feedback._Feedback__on_quit()
                # Load the default dummy Feedback
                self.feedback = Feedback(self.pp)
            elif e.subtype == Event.SEND_INIT:
                self.logger.info("Received SEND_INIT signal")
                # Working with old Feedback!
                self.feedback._Feedback__on_quit()
                self.load_feedback()
                # Proably a new one!
                self.feedback._Feedback__on_init()
                self.feedback._Feedback__on_interaction_event(e.data)
            else:
                self.logger.info("Received generic interaction signal")
        else:
            self.logger.warning("Received unknown event type: %i" % d)
        
        
    def main(self):
        """Start the Feedback Controller."""
        thread.start_new_thread(self.interaction_signal_loop, ())
        thread.start_new_thread(self.control_signal_loop, ())
        self.main_loop()
        
        
    def load_feedback(self):
        """
        Tries to find and load the feedback in the Feedbacks package. If the
        desired feedback does not exist, load the dummy feedback as fallback.
        """
        try:
            name = "Feedbacks."+getattr(self.feedback, self.feedback.PREFIX+"type")
            mod = __import__(name)
            components = name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            self.feedback = getattr(mod, components[-1])(self.pp)
        except:
            self.logger.warning("Unable to load Feedback, falling back to dummy.")
            self.logger.warning(traceback.format_exc())
            self.feedback = Feedback(self.pp)

    def main_loop(self):
        """
        Main event loop of the FB controller. 
        Waits for network or feedback events and deligates them to the apropiate
        places.
        """
        self.logger.info("Entering main loop.")
        while 1:
            e = self.q.get()
            self.handle_event(e)
        self.logger.info("Left main loop.")
        
    def process_interaction_signal(self, dgram):
        try:
            statements = self.decoder.decode_interaction_packet(dgram)
        except BadMagicError, e:
            self.logger.warning("Received interaction signal with bad magic: %x" % e.magic)
        except BadPacketSizeError, e:
            self.logger.warning("Received interaction signal with bad packet size. Should be %i, but was %i" % (e.shouldSize, e.isSize))
        else:
            self.logger.info("received %s" % str(statements))
            # Possible Signals are:
            # Send+Init, Send, Start, Pause and Quit
            play, pause, run_false, loop_false = False, False, False, False
            time = 0.0
            for var in statements:
                self.logger.debug("Analyzing statement: %s" % str(var))
                val = statements[var]
                if var == 'feedback_opt.status':
                    if val == 'play':
                        play = True
                    elif val == 'pause':
                        pause = True
                elif var == 'run' and val == False:
                    run_false = True
                elif var == 'loop' and val == False:
                    loop_false = True
            subtype = None
            if play:
                subtype = Event.PLAY
            elif pause:
                subtype = Event.PAUSE
            elif loop_false and run_false:
                subtype = Event.QUIT
            elif loop_false:
                subtype = Event.SEND_INIT

            return Event(Event.INTERACTION_EVENT, statements, subtype)
        return None


    def process_control_signal(self, dgram):
        try:
            data = self.decoder.decode_control_packet(dgram)
        except BadMagicError, e:
            self.logger.warning("Received control signal with bad magic: %x" % e.magic)
        except BadPacketSizeError, e:
            self.logger.warning("Received control signal with bad packet size. Should be %i, but was %i" % (e.shouldSize, e.isSize))
        else:
            self.logger.info("received %s" % str(data))

            return Event(Event.CONTROL_EVENT, data)
        return None

    
    def interaction_signal_loop(self):
        """Set up a socket for the interaction signal and listen on it."""
        # Setup socket for Interaction Signal.
        is_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        is_socket.bind( ('', IS_PORT) )
        self.logger.info("Entering interaction signal loop.")
        while 1:
            dgram = is_socket.recv(IS_BUFFER_SIZE)
            e = self.process_interaction_signal(dgram)
            if e:
                self.q.put(e)
        self.logger.info("Left interaction signal loop.")
        is_socket.close()
    
    def control_signal_loop(self):
        """Set up a socket for the control signal and listen on it."""
        # Setup socket for Control Signal.
        cs_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cs_socket.bind( ('', CS_PORT) )
        self.logger.info("Entering control signal loop.")
        while 1:
            dgram = cs_socket.recv(CS_BUFFER_SIZE)
            e = self.process_control_signal(dgram)
            if e:
                self.q.put(e)
        self.logger.info("Left control signal loop.")
        cs_socket.close()


class Event:
    """Represents an Event with a type and the data."""
    
    CONTROL_EVENT = 10
    INTERACTION_EVENT = 20

    PLAY = 21
    PAUSE = 22
    QUIT = 23
    SEND_INIT = 24
   
    
    def __init__(self, type, data, subtype=None):
        self.type = type
        self.data = data
        self.subtype = subtype
    
    
import asyncore

class Dispatcher(asyncore.dispatcher):
    """Dispatcher for the interaction signal."""
    
    def __init__(self, port, feedbackController):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", port))
        if port == IS_PORT:
            self.handle_read = self.handle_is_read
        elif port == CS_PORT:
            self.handle_read = self.handle_cs_read
        self.feedbackController = feedbackController
        
    def writable(self):
        return False

    def handle_connect(self):
        pass
        
    def handle_is_read(self):
        datagram = self.recv(IS_BUFFER_SIZE)
        self.feedbackController.on_is_signal(datagram)
            
    def handle_cs_read(self):
        datagram = self.recv(IS_BUFFER_SIZE)
        self.feedbackController.on_cs_signal(datagram)
        

class FeedbackController2(FeedbackController):
    """
    Non-threaded variant of the FeedbackController which uses select to poll
    the network interface asyncronously.
    """
    
    def on_is_signal(self, data):
        e = self.process_interaction_signal(data)
        if e:
            self.handle_event(e)
    
    def on_cs_signal(self, data):
        e = self.process_control_signal(data)
        if e:
            self.handle_event(e)


class FeedbackController3(FeedbackController):
    """
    Variant of the Feedback Controller where the Feedback runs in the main
    thread and everything else in other threads. Let's see how that turns out...
    """

    def __init__(self):
        FeedbackController.__init__(self)
        self.playEvent = threading.Event()
        
    def main_loop(self):
        while True:
            # Block until we received a play signal
            self.logger.debug("Waiting for play-event.")
            self.playEvent.wait()
            self.logger.debug("Got play-event, starting Feedback's on_play()")
            self.playEvent.clear()
            # run the Feedbacks on_play in our thread
            self.feedback._Feedback__on_play()
            self.logger.debug("Feedback's on_play terminated.")

    def on_is_signal(self, data):
        e = self.process_interaction_signal(data)
        if e:
            self.handle_event(e)
    
    def on_cs_signal(self, data):
        e = self.process_control_signal(data)
        if e:
            self.handle_event(e)
            
    def handle_event(self, e):
        if e.type == Event.CONTROL_EVENT:
            self.logger.info("Received control signal")
            self.feedback._Feedback__on_control_event(e.data)
        elif e.type == Event.INTERACTION_EVENT:
            # Check the subtype if available
            self.feedback._Feedback__on_interaction_event(e.data)
            if e.subtype == Event.PLAY:
                self.logger.info("Received PLAY signal")
                # Instead of calling on_play in this thread, signal the main
                # thread to run it for us.
                self.playEvent.set()
            elif e.subtype == Event.PAUSE:
                self.logger.info("Received PAUSE signal")
                self.feedback._Feedback__on_pause()
            elif e.subtype == Event.QUIT:
                self.logger.info("Received QUIT signal")
                self.feedback._Feedback__on_quit()
                # Load the default dummy Feedback
                self.feedback = Feedback(self.pp)
            elif e.subtype == Event.SEND_INIT:
                self.logger.info("Received SEND_INIT signal")
                # Working with old Feedback!
                self.feedback._Feedback__on_quit()
                self.load_feedback()
                # Proably a new one!
                self.feedback._Feedback__on_init()
                self.feedback._Feedback__on_interaction_event(e.data)
            else:
                self.logger.info("Received generic interaction signal")
        else:
            self.logger.warning("Received unknown event type: %i" % d)
    

def start_feedback_controller():
    FeedbackController().main()

    
def start_feedback_controller2():
    feedbackController = FeedbackController2()
    Dispatcher(IS_PORT, feedbackController)
    Dispatcher(CS_PORT, feedbackController)
    asyncore.loop()

import threading

def start_feedback_controller3():
    feedbackController = FeedbackController3()
    Dispatcher(IS_PORT, feedbackController)
    Dispatcher(CS_PORT, feedbackController)
    t = threading.Thread(target=asyncore.loop, args=())
    t.start()
    feedbackController.main_loop()

def stop_feedback_controller(): pass
def stop_feedback_controller2(): pass
def stop_feedback_controller3(): pass

start_fc = start_feedback_controller3
stop_fc = stop_feedback_controller3

if __name__ == "__main__":
    try:
        start_fc()
    #FIXME: Does not work with FeedbackController yet (but with FC2)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Caught KeyboardInterrupt or SystemExit, quitting")
        stop_fc()
        sys.exit()
    except:
        raise
