# testUdpDecoder.py -
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

import unittest
import struct

class UdpDecoderTestCase(unittest.TestCase):
    
    def setUp(self):
        self.decoder = UdpDecoder()

        
    def testCorrectControlPaket(self):
        """Should correctly decode control packet."""
        n, m = 5, 6
        l = []
        packet = struct.pack("=3i", self.decoder.MAGIC, n, m)
        for i in range(n*m):
            l.append(float(i))
            packet += struct.pack("=1d", float(i))
        n2, m2, data = self.decoder.decode_control_packet(packet)
        self.assertEqual((n,m)+tuple(l), (n2, m2) + data)


    def testCorrectInteractionPaket(self):
        """Should correctly decode interaction packet."""
        s = "s = 'foobar'; i = 2;\n"
        d = {'s': 'foobar', 'i':2}
        n, m = 1, len(s)
        packet = struct.pack("=3i", self.decoder.MAGIC, n, m)
        for c in s:
            packet += struct.pack("=1d", float(ord(c)))
        n2, m2, data = self.decoder.decode_interaction_packet(packet)
        self.assertEqual((n,m,d), (n2, m2, data))
        
        
    def testParseStatements(self):
        """A string of matlab statements should return a dict of var-val pairs."""
        s = '"a=1; b=2 ; c = 3;d = 4; s = \'somestring\'; l1 = []; l2 = [1, 2, 4]; \n"'
        d = {"a":1, "b":2, "c":3, "d":4, "s": 'somestring', "l1": [], "l2": [1, 2, 4]}
        d2 = self.decoder._UdpDecoder__parse_statements(s)
        self.assertEqual(d, d2)

    
    def testParseType(self):
        """Shoudl correctly detect all kinds of matlab types and convert them to python's equivalent."""
        list = [("'a'", "a"), 
                ("1", 1), 
                ("true", True), 
                ("[]", []), 
                ("[1, 2, 'foo', false]", [1, 2, "foo", False]),
                ("{}", []),
                ("{1, 2, 'foo', false}", [1, 2, "foo", False]),
                 # Don't check for nested lists for now since matlab don't seem
                # to support them anyways.
#                ("[1, 2, 'foo', false, [1, 2, 'foo', false, [1, 2, 'foo', false]]]", [1, 2, "foo", False, [1, 2, "foo", False, [1, 2, "foo", False]]]),
#                ("[[[]]]", [[[]]])
                ]
        for a, b in list:
            self.assertEqual(self.decoder._UdpDecoder__parse_type(a), b)

    def testBadMagic(self):
        """Should raise BadMagicError."""
        self.assertRaises(BadMagicError, self.decoder.decode_control_packet, struct.pack("=3i", 12345, 0, 0))
        
    
    def testBadPacketSize(self):
        """Should raise BadPacketSize."""
        self.assertRaises(BadPacketSizeError, self.decoder.decode_control_packet, struct.pack("=3i1d", self.decoder.MAGIC, 0, 0, 1.0))

        
suite = unittest.makeSuite(UdpDecoderTestCase)
