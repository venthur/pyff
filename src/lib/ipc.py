# ipc.py -
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


"""Inter Process Communication.

this module provides classes to ease the inter process communication (IPC)
between the Feedback Controller and the Feedbacks
"""


import asyncore
import asynchat
import socket
import cPickle as pickle
import logging

import bcixml


# delimiter for IPC messages.
TERMINATOR = "\r\n\r\n"
# Port for IPC connections
IPC_PORT = 12347
LOCALHOST = "127.0.0.1"

import thread

def ipcloop():
    """Start the IPC loop."""
    asyncore.loop()


def get_feedbackcontroller_connection():
    """Return a connection to the Feedback Controller."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((LOCALHOST, IPC_PORT))
    return sock


class IPCConnectionHandler(asyncore.dispatcher):
    """Waits for incoming connection requests and dispatches a
    FeedbackControllerIPCChannel.
    """

    def __init__(self, fc):
        asyncore.dispatcher.__init__(self)
        self.logger = logging.getLogger("IPCConnectionHandler")
        self.conn = None
        self.addr = None
        self.ipcchan = None
        self.fc = fc
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind((LOCALHOST, IPC_PORT))
        self.listen(5)

    def handle_accept(self):
        """Handle incoming connection from Feedback."""
        self.logger.debug("Accepting.")
        self.conn, self.addr = self.accept()
        self.ipcchan = FeedbackControllerIPCChannel(self.conn, self.fc)

    def handle_close(self):
        """Handle closing of connection."""
        self.logger.debug("Closing.")
        self.ipcchan = None

    def handle_error(self):
        """Handle error."""
        self.logger.error("Some error occurred, ignoring it.")

    def send_message(self, message):
        """Send the message via the currently open connection."""
        if self.ipcchan:
            self.ipcchan.send_message(message)
        else:
            raise Exception("No open IPC channel available.")

    def close_channel(self):
        """Close the channel to the Feedback."""
        self.logger.debug("Closing channel to Feedback.")
        self.ipcchan.close()



class IPCChannel(asynchat.async_chat):
    """IPC Channel.

    Base for the channels, the Feedback Controller and the Feedbacks need.

    This Class transparently takes care of de-/serialization of the data which
    goes through the IPC. Derived classes should implement::

        handle_message(self, message)

    to do something useful and use::

        send_message(self, message)

    for sending messages via IPC.

    """

    def __init__(self, conn):
        """Initialize the Channel, set terminator and clear input buffer."""
        asynchat.async_chat.__init__(self, conn)
        self.logger = logging.getLogger("IPCChannel")
        self.set_terminator(TERMINATOR)
        # input buffer
        self.ibuf = ""

    def collect_incoming_data(self, data):
        """Append incoming data to input buffer.

        :param data: Incoming data

        """
        self.ibuf += data

    def found_terminator(self):
        """Process message from peer."""
        dump = self.ibuf
        self.ibuf = ""
        ipcmessage = pickle.loads(dump)
        try:
            self.handle_message(ipcmessage)
        except:
            self.logger.exception("Handling an ICP message caused an exception:")

    def send_message(self, message):
        """Send message to peer.

        :param message: Message

        """
        dump = pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL)
        dump += TERMINATOR
        self.push(dump)

    def handle_close(self):
        """Handle closing of connection."""
        self.logger.debug("Closing Connection.")
        asynchat.async_chat.handle_close(self)


    def handle_message(self, message):
        """Do something with the received message.

        This method should be overwritten by derived classes.

        :param message: Message
        """
        pass


class FeedbackControllerIPCChannel(IPCChannel):
    """IPC Channel for Feedback Contoller's end."""

    def __init__(self, conn, fc):
        IPCChannel.__init__(self, conn)
        self.fc = fc

    def handle_message(self, message):
        """Handle message from Feedback.

        :param message: Message

        """
        self.fc.handle_signal(message)


class FeedbackIPCChannel(IPCChannel):
    """IPC Channel for Feedback's end."""

    def __init__(self, conn, feedback):
        IPCChannel.__init__(self, conn)
        self.feedback = feedback


    def handle_message(self, message):
        """Handle message from Feedback Controller.

        :param message: Message

        """
        self.feedback.logger.debug("Processing signal")

        if message.type == bcixml.CONTROL_SIGNAL:
            self.feedback._on_control_event(message.data)
            return

        cmd = message.commands[0][0] if len(message.commands) > 0 else None
        if cmd == bcixml.CMD_GET_VARIABLES:
            reply = bcixml.BciSignal({"variables" : self.feedback._get_variables()}, None,
                                     bcixml.REPLY_SIGNAL)
            reply.peeraddr = message.peeraddr
            self.feedback.logger.debug("Sending variables")
            self.send_message(reply)
        self.feedback._on_interaction_event(message.data)
        if cmd == bcixml.CMD_PLAY:
            self.feedback._playEvent.set()
        elif cmd == bcixml.CMD_PAUSE:
            self.feedback._on_pause()
        elif cmd == bcixml.CMD_STOP:
            self.feedback._on_stop()
        elif cmd == bcixml.CMD_QUIT:
            self.feedback._on_quit()
        elif cmd == bcixml.CMD_SEND_INIT:
            self.feedback._on_init()
        elif cmd == bcixml.CMD_SAVE_VARIABLES:
            filename = message.commands[0][1]['filename']
            self.feedback.save_variables(filename)
        elif cmd == bcixml.CMD_LOAD_VARIABLES:
            filename = message.commands[0][1]['filename']
            self.feedback.load_variables(filename)


