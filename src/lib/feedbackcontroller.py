# feedbackcontroller.py -
# Copyright (C) 2007-2009  Bastian Venthur
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


import socket
import threading
import logging
import traceback

try:
    import parallel
except ImportError:
    print "Unable to import parallel module, have you pyparallel installed?"
from processing import Pipe

from lib import bcinetwork
from lib import bcixml
from FeedbackBase.Feedback import Feedback
from lib.feedbackprocesscontroller import FeedbackProcessController


class FeedbackController(object):
    def __init__(self, plugin=None, fbpath=None):
        # Setup my stuff:
        self.logger = logging.getLogger("FeedbackController")
        self.encoder = bcixml.XmlEncoder()
        self.decoder = bcixml.XmlDecoder()
        # Set up the socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", bcinetwork.FC_PORT))
        self.socket.settimeout(1.0)
        # Set up the pipe
        self.pipe = Pipe()
        # Setup the parallel port
        self.pp = None
        try:
            self.pp = parallel.Parallel()
        except:
            self.logger.warning("Unable to open parallel port!")
        self.playEvent = threading.Event()
        if plugin:
            self.logger.debug("Loading plugin %s" % str(plugin))
            try:
                self.inject(plugin)
            except:
                self.logger.error(str(traceback.format_exc()))
        fbdirs = ["Feedbacks"]
        if fbpath:
            fbdirs.append(fbpath)
        fbProcCtrl = FeedbackProcessController(fbdirs, Feedback, 1)
        
        self.fc_data = {}
        
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
    def pre_quit(self): pass
    def post_quit(self): pass
#
# /Feedback Controller Plugin-Methods
#    

    SUPPORTED_PLUGIN_METHODS = ["pre_init", "post_init",
                                "pre_play", "post_play",
                                "pre_pause", "post_pause",
                                "pre_stop", "post_stop",
                                "pre_quit", "post_quit"]
    
    def inject(self, module):
        """Inject methods from module to Feedback Controller."""
        try:
            m = __import__(module, fromlist=[None])
        except ImportError:
            self.logger.info("Unable to import module %s, aborting injection." % str(module))
        else:
            for meth in FeedbackController.SUPPORTED_PLUGIN_METHODS:
                if hasattr(m, meth) and callable(getattr(m, meth)):
                    setattr(FeedbackController, meth, getattr(m, meth))
                    self.logger.info("Sucessfully injected: %s" % meth)
                else:
                    self.logger.debug("Unable to inject %s" % meth)
                    has = hasattr(m, meth)
                    call = False
                    if has:
                        call = callable(getattr(m, meth))
                    self.logger.debug("hassattr/callable: %s/%s" % (str(has), str(call)))
                    


    def start(self):
        """Start the Feedback Controllers activities."""
        self.logger.debug("Started I/O loop.")
        self.io_loop()
        self.logger.debug("Left I/O loop.")

    
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
            elif signal.type == bcixml.FC_SIGNAL:
                self._handle_fcs(signal)
            else:
                self.logger.warning("Unknown signal type, ignoring it. (%s)" % str(signal.type))
        except:
            self.logger.error("Handling is or cs caused an exception.")
            self.logger.error(traceback.format_exc())


    def _handle_fcs(self, signal):
        # We assume, that the signal only contains variables which are to set
        # in the Feedback Controller
        self.fc_data = signal.data.copy()
        

    def _handle_cs(self, signal):
        self.feedback._on_control_event(signal.data)

    
    def _handle_is(self, signal):
        self.logger.info("Got interaction signal: %s" % str(signal))
        cmd = None
        if len(signal.commands) > 0:
            cmd = signal.commands[0]
        # check if this signal is for the FC only (and not for the feedback)
        if cmd == bcixml.CMD_GET_FEEDBACKS:
            ip, port = signal.peeraddr[0], bcinetwork.GUI_PORT
            bcinetw = bcinetwork.BciNetwork(ip, port)
            answer = bcixml.BciSignal({"feedbacks" : self.feedbacks}, None, bcixml.INTERACTION_SIGNAL)
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
        
        self.feedback._on_interaction_event(signal.data)
        if cmd == bcixml.CMD_PLAY:
            self.logger.info("Received PLAY signal")
            self.pre_play()
            self.playEvent.set()
            self.post_play()
            #self.feedback._Feedback__on_play()
        elif cmd == bcixml.CMD_PAUSE:
            self.logger.info("Received PAUSE signal")
            self.pre_pause()
            self.feedback._on_pause()
            self.post_pause()
        elif cmd == bcixml.CMD_STOP:
            self.logger.info("Received STOP signal")
            self.pre_stop()
            self.feedback._on_stop()
            self.post_stop()
        elif cmd == bcixml.CMD_QUIT:
            self.logger.info("Received QUIT signal")
            self.pre_quit()
            self.feedback._on_quit()
            # Load the default dummy Feedback
            self.feedback = Feedback(self.pp)
            self.post_quit()
        elif cmd == bcixml.CMD_SEND_INIT:
            self.logger.info("Received SEND_INIT signal")
            # Working with old Feedback!
            self.feedback._on_quit()
            name = getattr(self.feedback, "_feedback")
            try:
                self.logger.debug("Trying to load feedback: %s" % str(name))
                self.feedback = self.pluginController.load_plugin(name)(self.pp)
            except:
                self.logger.error("Unable to load feedback: %s" % str(name))
                self.logger.error(traceback.format_exc())
                self.feedback = Feedback(self.pp)
            # Proably a new one!
            self.pre_init()
            self.feedback._on_init()
            self.post_init()
            self.feedback._on_interaction_event(signal.data)
        else:
            self.logger.info("Received generic interaction signal")
            
    def io_loop(self):
        timeout = 1.0
        while True:
            # check the socket for new data
            self.process_socket()
            # check the pipe for new data
            self.process_pipe()
            
    def process_socket(self):
        try:
            (data, address) = self.socket.recvfrom(bcinetwork.BUFFER_SIZE)
        except socket.timeout:
            # Currently no data available on the socket, this is ok
            return
        print "From socket: ", data, address
    
    def process_pipe(self):
        if not self.pipe[0].poll():
            # Currently no data available on the pipe, this is ok
            return
        data = self.pipe[0].recv()
        print "From pipe: ", str(data)

