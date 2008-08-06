# UdpDecoder.py
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

import logging
import struct

class UdpDecoder:
    
    def __init__(self):
        self.logger = logging.getLogger('FC.UdpDecoder')
        self.logger.debug("Loaded my logger.")

        self.headerFormat = "=3i"
        self.headerSize = struct.calcsize(self.headerFormat)
        
        self.MAGIC = 0xb411510

    
    def decode_interaction_packet(self, packet):
        """Take raw packet and return tuple (n, m, signal)"""
        payload = self.__unpack_packet(packet)
        signal = "".join(map(chr, map(int, payload)))
        payload = self.__parse_statements(signal)
        self.logger.debug("Received interaction signal: %s" % signal)
        return payload
 
    
    def decode_control_packet(self, packet):
        """Take raw packet and return tuple (n, m, payload)"""
        payload = self.__unpack_packet(packet)
        self.logger.debug("Received control signal: %s" % str(payload))
        return payload
    
    
    def __unpack_packet(self, packet):
        """Take packet, check magic, unpack data and return tuple (n, m, payload)."""
        (magic, n, m) = struct.unpack(self.headerFormat, packet[0:self.headerSize])
        
        if magic != self.MAGIC:
            raise BadMagicError(magic)
        
        payloadLength = struct.calcsize("="+str(n*m)+"d")
        
        # [FIXME] Just for testing purpose -- remove in final release
        #if len(packet[self.headerSize:]) > payloadLength:
        #    packet = packet[0:self.headerSize+payloadLength]
        
        if len(packet[self.headerSize:]) != payloadLength:
            raise BadPacketSizeError(n*m, payloadLength)
        
        payload = struct.unpack("="+str(n*m)+"d", packet[self.headerSize:])
        return payload
    
    
    def __parse_type(self, val):
        """Parse a matlab variable string and return the correct python type"""
        val = val.strip()
        try:
            # String
            if val.startswith("'") and val.endswith("'"):
                val = val.strip("'")
            # Boolean
            elif val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            # List
            elif val.startswith("[") and val.endswith("]"):
                tmp = val.lstrip("[").rstrip("]").split(",")
                val = [self.__parse_type(i) for i in tmp if i != ""]
            # List2
            elif val.startswith("{") and val.endswith("}"):
                tmp = val.lstrip("{").rstrip("}").split(",")
                val = [self.__parse_type(i) for i in tmp if i != ""]
            # Integer
            elif val.find(".") == -1:
                val = int(val)
            # Default: Float
            else:
                val = float(val)
        except ValueError:
            self.logger.warning("Unable to Parse: %s, ignoring it." % val)
        except Exception, e:
            self.logger.warning("Unexpected Exception caught: %s." % str(e))
        else:
            return val
    
    
    def __parse_statements(self, string):
        """Parse matlab statements and return a Dictionary with parameter-value pairs."""
        string2 = string.strip('"')
        d = dict()
        for statement in string2.split(";"):
            tokens = statement.split("=")
            tokens = [i.strip() for i in tokens]
            while len(tokens) >= 2:
                var = tokens.pop(0)
                val = tokens.pop(0)
                d[var] = self.__parse_type(val)
            if len(tokens) > 0 and len(statement.strip()) > 0:
                self.logger.warning("List of tokens not empty: %s, the statement was: %s, stripped version is: %s" % (str(tokens), str(string), str(string2)))
        return d
            

class BadMagicError(Exception):
    def __init__(self, magic):
        self.magic = magic


class BadPacketSizeError(Exception):
    def __init__(self, shouldSize, isSize):
        self.shouldSize = shouldSize
        self.isSize = isSize
