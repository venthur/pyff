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
        self.fbProcCtrl = FeedbackProcessController(fbdirs, Feedback, 1)
        
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

    
    def handle_signal(self, signal):
        # check our signal if it contains anything useful, if not drop it and
        # print a warning
        try:
            if signal.type == bcixml.REPLY_SIGNAL:
                self.send_to_peer(signal)
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
        # We don't care about control signals, send it to the feedback
        self.send_to_feedback(signal)

    
    def _handle_is(self, signal):
        self.logger.info("Got interaction signal: %s" % str(signal))
        cmd = signal.commands[0] if len(signal.commands) > 0 else None
        
        # A few commands need to be handled by the Feedback Controller, the
        # rest goes to the Feedback
        if cmd == bcixml.CMD_GET_FEEDBACKS:
            reply = bcixml.BciSignal({"feedbacks" : self.fbProcCtrl.get_feedbacks()}, 
                                     None, bcixml.REPLY_SIGNAL)
            reply.peeraddr = signal.peeraddr
            self.send_to_peer(reply)
            return
        elif cmd == bcixml.CMD_GET_VARIABLES:
            # Put it in the pipe and hope that the reply will appear on our end.
            self.send_to_feedback(signal)
            return

        self.send_to_feedback(signal)
        if cmd == bcixml.CMD_QUIT:
            self.send_to_feedback(signal)
            self.fbProcCtrl.stop_feedback()
        elif cmd == bcixml.CMD_SEND_INIT:
            name = signal.data["_feedback"]
            self.fbProcCtrl.start_feedback(name)
            
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
        try:
            signal = self.decoder.decode_packet(data)
            signal.peeraddr = address
        except bcixml.DecodingError, e:
            # ok, somehow the parsing failed, just drop the packet and print a
            # warning
            self.logger.warning("Parsing of signal failed, ignoring it. (%s)" % str(e))
            return
        self.handle_signal(signal)
    
    def process_pipe(self):
        if not self.fbProcCtrl.poll():
            # Currently no data available on the pipe, this is ok
            return
        data = self.fbProcCtrl.receive_signal()
        self.handle_signal(data)

    def send_to_feedback(self, signal):
        # TODO: what if feedback does not exist?
        self.fbProcCtrl.send_signal(signal)
        
    def send_to_peer(self, signal):
        ip, port = signal.peeraddr[0], bcinetwork.GUI_PORT
        bcinetw = bcinetwork.BciNetwork(ip, port)
        self.logger.debug("Sending %s to %s:%s." % (str(signal), str(ip), str(port)))
        thread = threading.Thread(target=bcinetw.send_signal, args=(signal,))
        thread.run()

