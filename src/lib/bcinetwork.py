# bcinetwork.py -
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


import logging
import socket

from lib import bcixml


LOCALHOST = "127.0.0.1"
FC_PORT = 12345
GUI_PORT = 12346
BUFFER_SIZE = 65535
TIMEOUT = 2.0        # seconds to wait for reply


class BciNetwork(object):
    """Wrapper for Communication between Feedback Controller and GUI."""

    def __init__(self, ip, port, myport=None, protocol='bcixml'):
        """
        Initialize BciNetwork instance.

        :param ip: IP Address. If emtpy, assume localhost
        :type ip: str
        :param port: Port Number
        :type port: integer

        """
        self.logger = logging.getLogger("BciNetwork-%s:%s" % (str(ip), str(port)))
        self.logger.debug("BciNetwork initialized.")

        if ip == "":
            self.logger.debug("Got empty IP, assuming localhost.")
            ip = LOCALHOST

        self.addr = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.SEND_ONLY = True
        if myport != None:
            self.SEND_ONLY = False
            self.srvsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.srvsocket.bind((ip, myport))

        if protocol == 'json':
            self.xmlencoder = bcixml.JsonEncoder()
            self.xmldecoder = bcixml.JsonDecoder()
        else:
            # tobi and bcixml share the same encoder
            self.xmlencoder = bcixml.XmlEncoder()
            self.xmldecoder = bcixml.XmlDecoder()


    def getAvailableFeedbacks(self):
        """Get available Feedbacks from Feedback Controller.

        :returns: Feedbacks

        """
        signal = bcixml.BciSignal(None, [(bcixml.CMD_GET_FEEDBACKS, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

        data, addr = self.receive(TIMEOUT)
        if not data:
            self.logger.info("Did not receive an answer on getAvailableFeedbacks")
            return None
        answer = self.xmldecoder.decode_packet(data)
        return answer.data.get("feedbacks")


    def send_init(self, feedback):
        """Send 'send_init(feedback)' to Feedback Controller.

        :param feedback: Feedback

        """
        signal = bcixml.BciSignal({"_feedback": str(feedback)}, [(bcixml.CMD_SEND_INIT, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def play(self):
        """Send 'play' to Feedback Controller."""
        signal = bcixml.BciSignal(None, [(bcixml.CMD_PLAY, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def pause(self):
        """Send 'pause' to Feedback Controller."""
        signal = bcixml.BciSignal(None, [(bcixml.CMD_PAUSE, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def stop(self):
        """Send 'stop' to Feedback Controller."""
        signal = bcixml.BciSignal(None, [(bcixml.CMD_STOP, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def quit(self):
        """Send 'quit' to Feedback Controller."""
        signal = bcixml.BciSignal(None, [(bcixml.CMD_QUIT, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def quit_feedback_controller(self):
        """Send 'quit_feedback_controller' to Feedback Controller."""
        signal = bcixml.BciSignal(None, [(bcixml.CMD_QUIT_FEEDBACK_CONTROLLER, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def get_variables(self):
        """Get variables (name, type and value) from currently running Feedback.

        :returns: variables

        """
        signal = bcixml.BciSignal(None, [(bcixml.CMD_GET_VARIABLES, dict())], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

        data, addr = self.receive(TIMEOUT)
        if not data:
            self.logger.info("Did not receive answer on get_variables")
            return None
        answer = self.xmldecoder.decode_packet(data)
        return answer.data.get("variables")

    def save_configuration(self, filename):
        """Tell the Feedback to store it's variables to the given file.

        :param filename: Name of the file where to store the variables.
        :type filename: str

        """
        signal = bcixml.BciSignal(None, [(bcixml.CMD_SAVE_VARIABLES, {'filename' : filename})], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def load_configuration(self, filename):
        """Tell the Feedback to load variable values from given file.

        :param filename: Name of the file where to load the variables from
        :type filename: str

        """
        signal = bcixml.BciSignal(None, [(bcixml.CMD_LOAD_VARIABLES,
            {'filename' : filename})], bcixml.INTERACTION_SIGNAL)
        self.send_signal(signal)

    def send_signal(self, signal):
        """Send a signal.

        :param signal: Signal

        """
        xml = self.xmlencoder.encode_packet(signal)
        self.socket.sendto(xml, self.addr)

    def receive(self, timeout):
        """Receive a signal.

        :param timeout: Timeout in seconds
        :type timeout: float

        """
        if self.SEND_ONLY:
            self.logger.error("Unable to receive data, am in send-only mode!")
            #FIXME: should throw an exception here!
            return None, None
        self.srvsocket.setblocking(False)
        self.srvsocket.settimeout(timeout)
        data, addr = None, None
        try:
            data, addr = self.srvsocket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            # do something!
            self.logger.warning("Receiving from FC failed (timeout).")
        return data, addr

