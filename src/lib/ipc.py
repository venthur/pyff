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


# delimiter for IPC messages.
TERMINATOR = "\r\n\r\n"
# Port for IPC connections
IPC_PORT = 12346


class IPCConnectionHandler(asyncore.dispatcher):
    """Waits for incoming connection requests and dispatches a 
    FeedbackControllerIPCChannel.
    """ 
    
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", IPC_PORT))
        self.listen(5)
        
    def handle_accept(self):
        """Handle incoming connection from Feedback."""
        conn, addr = self.accept()
        FeedbackControllerIPCChannel(conn)


class IPCChannel(asynchat.async_chat):
    """IPC Channel.
    
    Base for the channels, the Feedback Controller and the Feedbacks need.
    
    This Class transparently takes care of de-/serialization of the data which
    goes through the IPC. Derived classes should implement 
    
        handle_message(self, message)
        
    to do something useful and use
    
        send_message(self, message)
        
    for sending messages via IPC.
    """
    
    def __init__(self, conn):
        """Initialize the Channel, set terminator and clear input buffer."""
        asynchat.async_chat.__init__(self, conn)
        self.set_terminator(TERMINATOR)
        # input buffer
        self.ibuf = ""
        
    def collect_incoming_data(self, data):
        """Append incoming data to input buffer."""
        self.ibuf += data
        
    def found_terminator(self):
        """Process message from peer."""
        dump = self.ibuf
        self.ibuf = ""
        ipcmessage = pickle.loads(dump)
        self.handle_message(ipcmessage)
        
    def send_message(self, message):
        """Send message to peer."""
        dump = pickle.dumps(message, protocol=pickle.HIGHEST_PROTOCOL)
        dump += TERMINATOR
        self.push(dump)

    def handle_message(self, message):
        """Do something with the received message.
        
        This method should be overwritten by derived classes."""
        pass


class FeedbackControllerIPCChannel(IPCChannel):
    """IPC Channel for Feedback Contoller's end."""

    def handle_message(self, message):
        """Handle message from Feedback."""
        print message
        

class FeedbackIPCChannel(IPCChannel):
    """IPC Channel for Feedback's end."""

    def handle_message(self, message):
        """Handle message from Feedback Controller."""
        print message
        
    


