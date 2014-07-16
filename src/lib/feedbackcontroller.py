# feedbackcontroller.py -
# Copyright (C) 2007-2014  Bastian Venthur
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
import logging
import sys
import asyncore

from lib import bcinetwork
from lib import bcixml
from FeedbackBase.Feedback import Feedback
from lib.feedbackprocesscontroller import FeedbackProcessController
import ipc


class FeedbackController(object):
    """Feedback Controller.

    Controlls the loading, unloading, starting, pausing and stopping of the
    Feedbacks. Can query the Feedback for it's variables and can as well set
    them.
    """
    def __init__(self, fbpath=None, port=None, protocol='bcixml'):
        # Setup my stuff:
        self.logger = logging.getLogger("FeedbackController")
        # Set up the socket
        self.ipcchannel = ipc.IPCConnectionHandler(self)
        self.udpconnectionhandler = UDPDispatcher(self, protocol)
        # Windows only, set the parallel port port
        self.ppport = port
        fbdirs = ["Feedbacks"]
        if fbpath:
            fbdirs.extend(fbpath)
        self.fbProcCtrl = FeedbackProcessController(fbdirs, Feedback, 1)
        self.fc_data = {}


    def start(self):
        """Start the Feedback Controller's activities."""
        self.logger.debug("Started mainloop.")
        ipc.ipcloop()
        self.logger.debug("Left mainloop.")


    def stop(self):
        """Stop the Feedback Controller's activities."""
        self.fbProcCtrl.stop_feedback()
        asyncore.close_all()


    def handle_signal(self, signal):
        """Handle incoming signal.

        :param signal: signal

        """
        # check our signal if it contains anything useful, if not drop it and
        # print a warning
        try:
            if signal.type == bcixml.REPLY_SIGNAL:
                self.send_to_peer(signal)
            elif signal.type == bcixml.CONTROL_SIGNAL:
                self._handle_cs(signal)
            elif signal.type == bcixml.INTERACTION_SIGNAL:
                self._handle_is(signal)
            else:
                self.logger.warning("Unknown signal type, ignoring it. (%s)" % str(signal.type))
        except:
            self.logger.exception("Handling IS or CS caused an exception.")


    def _handle_cs(self, signal):
        """Handle Control Signal."""
        # We don't care about control signals, send it to the feedback
        self.send_to_feedback(signal)


    def _handle_is(self, signal):
        """Handle Interaction Signal."""
        self.logger.info("Got interaction signal: %s" % str(signal))
        cmd = signal.commands[0][0] if len(signal.commands) > 0 else None

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
        elif cmd == bcixml.CMD_QUIT_FEEDBACK_CONTROLLER:
            self.stop()

        if cmd == bcixml.CMD_QUIT:
            self.send_to_feedback(signal)
            self.ipcchannel.close_channel()
            self.fbProcCtrl.stop_feedback()
        elif cmd == bcixml.CMD_SEND_INIT:
            name = signal.data["_feedback"]
            self.fbProcCtrl.start_feedback(name, port=self.ppport)
        else:
            self.send_to_feedback(signal)


    def send_to_feedback(self, signal):
        """Send data to the feedback.

        :param signal: signal

        """
        try:
            self.ipcchannel.send_message(signal)
        except:
            self.logger.exception("Couldn't send data to Feedback.")


    def send_to_peer(self, signal):
        """Send signal to peer.

        :param signal: signal

        """
        self.udpconnectionhandler.send_signal(signal)


class UDPDispatcher(asyncore.dispatcher):
    """UDP Message Hanlder of the Feedback Controller."""

    def __init__(self, fc, protocol):
        asyncore.dispatcher.__init__(self)
        self.fc = fc
        if protocol == 'json':
            self.decoder = bcixml.JsonDecoder()
            self.encoder = bcixml.JsonEncoder()
        elif protocol == 'tobixml':
            # tobi and bcixml share the same encoder
            self.decoder = bcixml.TobiXmlDecoder()
            self.encoder = bcixml.XmlEncoder()
        else:
            self.decoder = bcixml.XmlDecoder()
            self.encoder = bcixml.XmlEncoder()
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind((bcinetwork.LOCALHOST, bcinetwork.FC_PORT))

    def send_signal(self, signal):
        """Send signal to the GUI."""
        data = self.encoder.encode_packet(signal)
        self.socket.sendto(data, (signal.peeraddr[0], bcinetwork.GUI_PORT))

    def handle_connect(self): pass

    def writable(self):
        return False

    def handle_read(self):
        """Handle incoming signals.

        Takes incoming signals, decodes them and forwards them to the
        Feedback Controller.
        """
        try:
            data, address = self.recvfrom(bcinetwork.BUFFER_SIZE)
            signal = self.decoder.decode_packet(data)
            signal.peeraddr = address
            self.fc.handle_signal(signal)
        except:
            self.fc.logger.exception("Handling incoming signal caused an exception:")

