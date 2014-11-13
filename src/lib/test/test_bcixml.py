# testbcixml.py -
# encoding: utf8
# Copyright (C) 2008-2009  Bastian Venthur
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


import unittest
from xml.dom import minidom, Node

from lib import bcixml


class BcixmlTestCase(unittest.TestCase):

    def setUp(self):
        self.encoder = bcixml.XmlEncoder()
        self.decoder = bcixml.XmlDecoder()

    def testBoolean(self):
        """Should correctly en/decode Boolean."""
        self.__convert_and_compare("somename", True)
        self.__convert_and_compare("somename", False)

    def testInteger(self):
        """Should correctly en/decode Integer."""
        self.__convert_and_compare("somename", 1)

    def testFloat(self):
        """Should correctly en/decode Float."""
        self.__convert_and_compare("somename", 1.0)

    def testLong(self):
        """Should correctly en/decode Long."""
        self.__convert_and_compare("somename", long(1))

    def testComplex(self):
        """Should correctly en/decode Complex."""
        self.__convert_and_compare("somename", 1+0j)

    def testString(self):
        """Should correctly en/decode String."""
        self.__convert_and_compare("somename", "foo")

    def testUnicode(self):
        """Should correctly en/decode Unicode."""
        self.__convert_and_compare("somename", u"ß")

    def testNone(self):
        """Should correctly en/decode None."""
        self.__convert_and_compare("somename", None)

    def testList(self):
        """Should correctly en/decode List."""
        self.__convert_and_compare("somename", [1,2,3,4,5])
        self.__convert_and_compare("somename", [])
        self.__convert_and_compare("somename", [1])

    def testTuple(self):
        """Should correctly en/decode Tuple."""
        self.__convert_and_compare("somename", (1,2,3,4,5))
        self.__convert_and_compare("somename", ())
        self.__convert_and_compare("somename", (1,))

    def testSet(self):
        """Should correctly en/decode Set."""
        self.__convert_and_compare("somename", set([1,2,3]))

    def testFrozenset(self):
        """Should correctly en/decode Frozenset."""
        self.__convert_and_compare("somename", frozenset([1,2,3]))

    def testDict(self):
        """Should correctly en/decode Dict."""
        self.__convert_and_compare("somename", {"foo" : 1, "bar" : 2, "baz" : 3})

    def testNestedLists(self):
        """Should correctly en/decode nested Lists."""
        self.__convert_and_compare("somename", [[], [1], [1, [1,2]]])

    def testNestedTuples(self):
        """Should correctly en/decode nested Tuples."""
        self.__convert_and_compare("somename", ((), (1), (1, (1,2))))

    def testNestedDicts(self):
        """Should correctly en/decode nested Dicts."""
        self.__convert_and_compare("somename", {"foo" : 1, "bratwurst" : {"bar" : 2, "baz" : 3}})


    def testUnsupported(self):
        """Should ignore unsupported Datatypes."""
        class Foo(object):
            pass
        f = Foo()
        d = {"foo" : f}
        d2 = {}
        self.__convert_and_compare("somename", d, d2)
        #self.__convert_and_compare("somename", [f], [])

    def testEncodeUnsupportedSignalType(self):
        """Should throw an Exception on encoding an unknown signal type."""
        signal = bcixml.BciSignal(None, None, "foo")
        self.assertRaises(bcixml.EncodingError, self.encoder.encode_packet, signal)


    def testDecodeUnsupportedSignalType(self):
        """Should throw an Exception on decoding an unknown signal type."""
        xml = """<?xml version="1.0" ?><bci-signal version="1.0"><foo/></bci-signal>"""
        self.assertRaises(bcixml.DecodingError, self.decoder.decode_packet, xml)

#
# some pitfalls...
#
    def testFalseBoolean(self):
        """Should correctly detect booleans with value "False"."""
        xml = '<boolean name="foo" value="False"/>'
        dom = minidom.parseString(xml)
        type, (name, value) = self.decoder._XmlDecoder__parse_element(dom.documentElement)
        self.assertEqual(name, "foo")
        self.assertEqual(value, False)


    def __convert_and_compare(self, name, value, value2=None):
        signal = bcixml.BciSignal({name : value}, None, bcixml.INTERACTION_SIGNAL)
        xml = self.encoder.encode_packet(signal)
        signal2 = self.decoder.decode_packet(xml)
        if value2 == None:
            value2 = value
        self.assertTrue(signal2.data.has_key(name))
        self.assertEqual(signal2.data[name], value2)
        self.assertEqual(type(signal2.data[name]), type(value2))


    def testInteraction_Signal(self):
        """Should support Interaction Signal type."""
        data = {"foo" : "bar", "baz" : 3}
        signal = bcixml.BciSignal(data, None, bcixml.INTERACTION_SIGNAL)
        xml = self.encoder.encode_packet(signal)
        signal2 = self.decoder.decode_packet(xml)
        self.assertEqual(signal2.type, signal.type)
        self.assertEqual(signal2.data, data)


    def testControl_Signal(self):
        """Should support Control Signal type."""
        data = {"foo" : "bar", "baz" : 3}
        signal = bcixml.BciSignal(data, None, bcixml.CONTROL_SIGNAL)
        xml = self.encoder.encode_packet(signal)
        signal2 = self.decoder.decode_packet(xml)
        self.assertEqual(signal2.type, signal.type)
        self.assertEqual(signal2.data, data)

    def test_Reply_Signal(self):
        """Should support Reply Signal type."""
        signal = bcixml.BciSignal(None, None, bcixml.REPLY_SIGNAL)
        xml = self.encoder.encode_packet(signal)
        signal2 = self.decoder.decode_packet(xml)
        self.assertEqual(signal.type, signal2.type)

    def test_Command(self):
        """Should support Commands with arguments."""
        signal = bcixml.BciSignal(None, [['foo', dict()]], bcixml.INTERACTION_SIGNAL)
        xml = self.encoder.encode_packet(signal)
        signal2 = self.decoder.decode_packet(xml)
        self.assertEqual(signal.commands, signal2.commands)

#suite = unittest.makeSuite(BcixmlTestCase)
def suite():
    testSuite = unittest.makeSuite(BcixmlTestCase)
    return testSuite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    main()

