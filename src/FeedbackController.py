#!/usr/bin/env python
# coding: utf8

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

from lib import bcinetwork
from lib import bcixml
from FeedbackBase.Feedback import Feedback

try:
    import parallel
except ImportError:
    print "Unable to import parallel module, have you pyparallel installed?"

import socket
import asyncore
import threading
import logging
import sys
import os
import traceback
from optparse import OptionParser

class FeedbackController(object):
    def __init__(self):
        # Setup my stuff:
        self.logger = logging.getLogger("FeedbackController")
        self.encoder = bcixml.XmlEncoder()
        self.decoder = bcixml.XmlDecoder()
        self.feedbacks = self.get_feedbacks()
        self.logger.info("Registered the following Feedbacks:")
        for i in self.feedbacks:
            self.logger.info("\t%s" % str(i))
        # Setup the parallel port
        self.pp = None
        try:
            self.pp = parallel.Parallel()
        except:
            self.logger.error("Unable to open parallel port!")
        self.feedback = Feedback(self.pp)
        self.playEvent = threading.Event()
        self.inject("FeedbackControllerPlugins")
        
#
# Feedback Controller Plugin-Methods
#    
    def pre_init(self): pass
    def post_init(self): pass
    def pre_play(self): pass
    def post_play(self): pass
    def pre_pause(self): pass
    def post_pause(self): pass
    def pre_stop(self): pass
    def post_stop(self): pass
#
# /Feedback Controller Plugin-Methods
#    

    SUPPORTED_PLUGIN_METHODS = ["pre_init", "post_init", 
                                "pre_play", "post_play", 
                                "pre_pause", "post_pause",
                                "pre_stop", "post_stop"]
    
    def inject(self, module):
        """Inject methods from module to Feedback Controller."""
        
        try:
            m = __import__(module, fromlist=[None])
        except ImportError:
            self.logger.error("Unable to import module, aborting injection.")
        else:
            for meth in FeedbackController.SUPPORTED_PLUGIN_METHODS:
                if hasattr(m, meth) and callable(getattr(m, meth)):
                    setattr(FeedbackController, meth, getattr(m, meth))
                else:
                    self.logger.error("Unable to inject %s" % meth)
                    has = hasattr(m, meth)
                    call = False
                    if has:
                        call = callable(getattr(m, meth))
                    self.logger.error("hassattr/callable: %s/%s" % (str(has), str(call)))
                    


    def start(self):
        """Start the Feedback Controllers activities."""
        
        # Listen on the network in a second thread
        Dispatcher(bcinetwork.FC_PORT, self)
        self.networkThread = threading.Thread(target=asyncore.loop, args=())
        self.networkThread.start()
        
        # start my main loop
        self.logger.debug("Started main loop.")
        self.main_loop()
        self.logger.debug("Left main loop.")

    
    def on_signal(self, address, datagram):
        signal = None
        try:
            signal = self.decoder.decode_packet(datagram)
            signal.peeraddr = address
        except bcixml.DecodingError, e:
            # ok, somehow the parsing failed, just drop the packet and print a
            # warning
            self.logger.warning("Parsing of signal failed, ignoring it. (%s)" % str(e))
            return
        # check our signal if it contains anything useful, if not drop it and
        # print a warning
        try:
            if signal.type == bcixml.CONTROL_SIGNAL:
                self._handle_cs(signal)
            elif signal.type == bcixml.INTERACTION_SIGNAL:
                self._handle_is(signal)
            else:
                self.logger.warning("Unknown signal type, ignoring it. (%s)" % str(signal.type))
        except:
            self.logger.error("Ooops, handling is or cs caused an exception.")
            self.logger.error(traceback.format_exc())

        
    def main_loop(self):
        while True:
            # Block until we received a play signal
            self.logger.debug("Waiting for play-event.")
            self.playEvent.wait()
            self.logger.debug("Got play-event, starting Feedback's on_play()")
            self.playEvent.clear()
            # run the Feedbacks on_play in our thread
            self.feedback._Feedback__on_play()
            #self.call_method_safely(self.feedback._Feedback__on_play())
            self.logger.debug("Feedback's on_play terminated.")


    def _handle_cs(self, signal):
        self.feedback._Feedback__on_control_event(signal.data)

    
    def _handle_is(self, signal):
        self.logger.info("Got interaction signal: %s" % str(signal))
        cmd = None
        if len(signal.commands) > 0:
            cmd = signal.commands[0]
        # check if this signal is for the FC only (and not for the feedback)
        if cmd == bcixml.CMD_GET_FEEDBACKS:
            ip, port = signal.peeraddr[0], bcinetwork.GUI_PORT
            bcinetw = bcinetwork.BciNetwork(ip, port)
            answer = bcixml.BciSignal({"feedbacks" : self.feedbacks.keys()}, None, bcixml.INTERACTION_SIGNAL)
            self.logger.debug("Sending %s to %s:%s." % (str(answer), str(ip), str(port)))
            bcinetw.send_signal(answer)
            return
        elif cmd == bcixml.CMD_GET_VARIABLES:
            ip, port = signal.peeraddr[0], bcinetwork.GUI_PORT
            bcinetw = bcinetwork.BciNetwork(ip, port)
            answer = bcixml.BciSignal({"variables" : self.feedback.__dict__}, None, bcixml.INTERACTION_SIGNAL)
            self.logger.debug("Sending %s to %s:%s." % (str(answer), str(ip), str(port)))
            bcinetw.send_signal(answer)
            return
        
        self.feedback._Feedback__on_interaction_event(signal.data)
        if cmd == bcixml.CMD_PLAY:
            self.logger.info("Received PLAY signal")
            self.pre_play()
            self.playEvent.set()
            self.post_play()
            #self.feedback._Feedback__on_play()
        elif cmd == bcixml.CMD_PAUSE:
            self.logger.info("Received PAUSE signal")
            self.pre_pause()
            self.feedback._Feedback__on_pause()
            self.post_pause()
        elif cmd == bcixml.CMD_QUIT:
            self.logger.info("Received QUIT signal")
            self.pre_stop()
            self.feedback._Feedback__on_quit()
            # Load the default dummy Feedback
            self.feedback = Feedback(self.pp)
            self.post_stop()
        elif cmd == bcixml.CMD_SEND_INIT:
            self.logger.info("Received SEND_INIT signal")
            # Working with old Feedback!
            self.feedback._Feedback__on_quit()
            self.load_feedback()
            # Proably a new one!
            self.pre_init()
            self.feedback._Feedback__on_init()
            self.post_init()
            self.feedback._Feedback__on_interaction_event(signal.data)
        else:
            self.logger.info("Received generic interaction signal")

            
    def test_feedback(self, root, file):
        # remove trailing .py if present
        if file.lower().endswith(".py"):
            file2 = file[:-3]
        root = root.replace(os.sep, ".")
        while root.startswith("."):
            root = root[1:]
        if not root.endswith(".") and not file2.startswith("."):
            module = root + "." + file2
        else:
            module = root + file2
        valid, name = False, file2
        if name == "__init__":
            return False, name, module
        mod = None
        try:
            mod = __import__(module, fromlist=[None])
            #print "1/3: loaded module (%s)." % str(module)
            fb = getattr(mod, name)(None)
            #print "2/3: loaded feedback (%s)." % str(file2)
            if isinstance(fb, Feedback):
                #print "3/3: feedback is valid Feedback()"
                valid = True
        except:
            self.logger.warning("Ooops! Something went wrong loading the feedback: %s from module: %s" % (name, module))
            self.logger.warning(traceback.format_exc())
        del mod
        return valid, name, module

    
    def get_feedbacks(self):
        """Returns the valid feedbacks in this directory."""
        feedbacks = {}
        for root, dirs, files in os.walk("Feedbacks"):
            for file in files:
                if file.lower().endswith(".py"):
                    # ok we found a candidate, check if it's a valid feedback
                    isFeedback, name, module = self.test_feedback(root, file)
                    if isFeedback:
                        feedbacks[name] = module
        return feedbacks


    def load_feedback(self):
        """
        Tries to find and load the feedback in the Feedbacks package. If the
        desired feedback does not exist, load the dummy feedback as fallback.
        """
        name = getattr(self.feedback, "_feedback")
        module = self.feedbacks[name]
        
        self.logger.debug("Trying to load feedback: %s from module: %s." % (name, module))
        
        try:
            # check if desired module is alreadty loaded, if so just reload it
            if sys.modules.has_key(module):
                self.logger.debug("Feedback module %s already loaded, trying to reload it." % str(module))
                mod = reload(sys.modules[module])
            else:
                self.logger.debug("Loading module %s for the first time." % str(module))
                mod = __import__(module, fromlist=[None])
            self.feedback = getattr(mod, name)(self.pp)
        except:
            self.logger.warning("Unable to load Feedback, falling back to dummy.")
            self.logger.warning(traceback.format_exc())
            self.feedback = Feedback(self.pp)
            
        # TODO: Evalutate if this is really a good idea to wrap this method
        # arounda all Feedback-methods called by the Feedback Controller
#    def call_method_safely(self, method):
#        """A wrapper which encapsulates the method call in a try block."""
#        try:
#            method()
#        except:
#            self.logger.error("Caught an exception running the method, here is the stack trace. Moving on.")
#            self.logger.error(traceback.format_exc())
            


class Dispatcher(asyncore.dispatcher):
    def __init__(self, port, feedbackController):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", port))
        #self.handle_read = self.handle_read
        self.feedbackController = feedbackController
        
    def writable(self):
        return False

    def handle_connect(self):
        pass
        
    def handle_read(self):
        datagram = self.recv(bcinetwork.BUFFER_SIZE)
        self.feedbackController.on_signal(self.addr, datagram)    


def start_fc():
    fc = FeedbackController()
    fc.start()

def stop_fc():
    pass


def main():
    
    # Get Options
    description = """Feedback Controller"""
    usage = "%prog [Options]"
    version = """
Copyright (C) 2007-2008 Bastian Venthur <venthur at cs tu-berlin de>

Homepage: http://bbci.de/pyff

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
    parser = OptionParser(usage=usage, version=version, description=description)
    parser.add_option('-l', '--loglevel', type='choice', choices=['critical',
        'error', 'warning', 'info', 'debug', 'notset'], dest='loglevel',
        help='Which loglevel to use for everything but the Feedbacks. Valid loglevels are: critical, error, warning, info, debug and notset. [default: warning]',
        metavar='LEVEL')
    parser.add_option('--fb-loglevel', type='choice', choices=['critical',
        'error', 'warning', 'info', 'debug', 'notset'], dest='fbloglevel',
        help='Which loglevel to use for the Feedbacks. Valid loglevels are: critical, error, warning, info, debug and notset. [default: warning]',
        metavar='LEVEL')

    options, args = parser.parse_args()

    # Initialize logging
    str2loglevel = {'critical' : logging.CRITICAL,
                    'error'    : logging.ERROR,
                    'warning'  : logging.WARNING,
                    'info'     : logging.INFO,
                    'debug'    : logging.DEBUG,
                    'notset'   : logging.NOTSET}
    
    loglevel = str2loglevel.get(options.loglevel, logging.WARNING)
    fbloglevel = str2loglevel.get(options.fbloglevel, logging.WARNING)

    logging.basicConfig(level=loglevel, format='[%(threadName)-10s] %(name)-25s: %(levelname)-8s %(message)s')
    logging.info('Logger initialized with level %s.' % options.loglevel)
    logging.getLogger("FB").setLevel(fbloglevel)

    try:
        start_fc()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Caught keyboard interrupt or system exit; quitting")
        stop_fc()
        sys.exit()
    


if __name__ == '__main__':
    main()
