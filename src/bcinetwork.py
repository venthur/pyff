# bcinetwork.py -
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

import socket
import bcixml

LOCALHOST = "127.0.0.1"
FC_PORT = 12345
GUI_PORT = 12346
BUFFER_SIZE = 65535
TIMEOUT = 2.0        # seconds to wait for reply


class BciNetwork(object):
    
    def __init__(self, ip, port):
        self.addr = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.xmlencoder = bcixml.XmlEncoder()
        self.xmldecoder = bcixml.XmlDecoder()
        
        
    def getAvailableFeedbacks(self):
        signal = bcixml.BciSignal(None, [bcixml.CMD_GET_FEEDBACKS], bcixml.INTERACTION_SIGNAL)
        xml = self.xmlencoder.encode_packet(signal)
        self.send(xml)
        
        data, addr = self.receive(TIMEOUT)
        answer = self.xmldecoder.decode_packet(data)
        print "Received answer: %s" % str(answer)
        return answer.data.get("feedbacks")
    
    
    def send_init(self, feedback):
        signal = bcixml.BciSignal({"feedback": str(feedback)}, [bcixml.CMD_SEND_INIT], bcixml.INTERACTION_SIGNAL)
        xml = self.xmlencoder.encode_packet(signal)
        self.send(xml)

    def play(self):
        signal = bcixml.BciSignal(None, [bcixml.CMD_PLAY], bcixml.INTERACTION_SIGNAL)
        xml = self.xmlencoder.encode_packet(signal)
        self.send(xml)

    def pause(self):
        signal = bcixml.BciSignal(None, [bcixml.CMD_PAUSE], bcixml.INTERACTION_SIGNAL)
        xml = self.xmlencoder.encode_packet(signal)
        self.send(xml)

    def stop(self):
        signal = bcixml.BciSignal(None, [bcixml.CMD_QUIT], bcixml.INTERACTION_SIGNAL)
        xml = self.xmlencoder.encode_packet(signal)
        self.send(xml)


    def send_signal(self, signal):
        xml = self.xmlencoder.encode_packet(signal)
        self.send(xml)


    def send(self, string):
        self.socket.sendto(string, self.addr)
        
    
    def receive(self, timeout):
        srvsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        srvsocket.bind(('', GUI_PORT))
        srvsocket.setblocking(False)
        srvsocket.settimeout(timeout)
        data, addr = None, None
        try:
            data, addr = srvsocket.recvfrom(BUFFER_SIZE)
        except socket.timeout:
            # do something!
            print "Receiving from FC failed (timeout)."
            srvsocket.close()
        srvsocket.close()
        return data, addr
        