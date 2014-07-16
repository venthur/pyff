# bcixml.py -
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

"""Encoding and decoding of bci-xml packages."""


import logging
import sys
from xml.dom import minidom, Node
import json

from lib import pylibtobiic


XML_ROOT = "bci-signal"
VERSION = "version"
CURRENT_VERSION = "1.0"
SUPPORTED_VERSIONS = ("1.0")

CONTROL_SIGNAL = "control-signal"
INTERACTION_SIGNAL = "interaction-signal"
REPLY_SIGNAL = "reply"

NAME = "name"
VALUE = "value"

COMMAND = 0
VARIABLE = 1

TRUE_VALUE = ("True", "true", "1")
FALSE_VALUE = ("False", "false", "0")

BOOLEAN_TYPE = ("b", "bool", "boolean")
INTEGER_TYPE = ("i", "int", "integer")
FLOAT_TYPE = ("f", "float")
LONG_TYPE = ("l", "long")
COMPLEX_TYPE = ("c", "cmplx", "complex")
STRING_TYPE = ("s", "str", "string")
UNICODE_TYPE = ('u', 'unicode')
LIST_TYPE = ("list",)
TUPLE_TYPE = ("tuple",)
SET_TYPE = ("set",)
FROZENSET_TYPE = ("frozenset",)
DICT_TYPE = ("dict",)
NONE_TYPE = ("none",)
UNSUPPORTED_TYPE = ("unsupported",)
COMMAND_TYPE = ("command",)

CMD_GET_FEEDBACKS = "getfeedbacks"        # tell the fc to send the list of available feedbacks
CMD_PLAY = 'play'
CMD_PAUSE = 'pause'
CMD_STOP = 'stop'
CMD_QUIT = 'quit'
CMD_SEND_INIT = 'sendinit'
CMD_GET_VARIABLES = 'getvariables'
CMD_SAVE_VARIABLES = 'savevariables'
CMD_LOAD_VARIABLES = 'loadvariables'
CMD_QUIT_FEEDBACK_CONTROLLER = 'quitfeedbackcontroller'


class XmlDecoder(object):
    """Parses XML strings and returns BciSignal containing the data of the
    signal.

    Usage::

        decoder = XmlDecoder()
        try:
            bcisignal = decoder.decode_packet(xml)
        except DecodingError:
            ...

    """


    def __init__(self):
        self.logger = logging.getLogger("XmlDecoder")


    def decode_packet(self, packet):
        """Parse the XML string and return a BciSignal.

        :param packet: XML Packet
        :type packet: str
        :returns: BciSignal
        :raises: A DecodingError is raised when the parsing of the packet failed.

        """
        dom = None
        try:
            dom = minidom.parseString(packet)
        except:
            raise DecodingError("Not XML at all! (%s)" % unicode(packet))
        root = dom.documentElement
        l = []    # for the variables
        c = []    # for the commands
        t = None  # for the type
        for node in root.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName in [INTERACTION_SIGNAL, CONTROL_SIGNAL, REPLY_SIGNAL]:
                    t = node.nodeName
                else:
                    self.logger.warning("Received a signal which contains neither an interaction- nor a control-signal. (%s)" % str(node.nodeName))
                    raise DecodingError("Received a signal which contains neither an interaction- nor a control-signal. (%s)" % str(node.nodeName))
                for node2 in node.childNodes:
                    if node2.nodeType == Node.ELEMENT_NODE:
                        type, value = self.__parse_element(node2)
                        if type == VARIABLE:
                            l.append(value)
                        elif type == COMMAND:
                            c.append(value)
                        else:
                            raise DecodingError("Unknown type (%s)" % str(type))
        return BciSignal(dict(l), c, t)


    def __parse_element(self, element):
        """Parse the element and return a dictionary with the data."""

        type = element.nodeName
        name = self.__get(element, NAME)
        value = self.__get(element, VALUE)

        if type in BOOLEAN_TYPE:
            if value in TRUE_VALUE:
                return VARIABLE, (name, bool(True))
            elif value in FALSE_VALUE:
                return VARIABLE, (name, bool(False))
            else:
                raise DecodingError("Unknown boolean value: %s" % str(value))
        elif type in INTEGER_TYPE:
            return VARIABLE, (name, int(value))
        elif type in FLOAT_TYPE:
            return VARIABLE, (name, float(value))
        elif type in LONG_TYPE:
            return VARIABLE, (name, long(value))
        elif type in COMPLEX_TYPE:
            if value.startswith("(") and value.endswith(")"):
                value = value[1:-1]
            return VARIABLE, (name, complex(value))
        elif type in STRING_TYPE:
            return VARIABLE, (name, str(value))
        elif type in UNICODE_TYPE:
            return VARIABLE, (name, unicode(value))
        elif type in LIST_TYPE:
            l = list()
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    l.append(self.__parse_element(node)[-1][-1])
            return VARIABLE, (name, l)
        elif type in TUPLE_TYPE:
            l = list()
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    l.append(self.__parse_element(node)[-1][-1])
            return VARIABLE, (name, tuple(l))
        elif type in SET_TYPE:
            l = list()
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    l.append(self.__parse_element(node)[-1][-1])
            return VARIABLE, (name, set(l))
        elif type in FROZENSET_TYPE:
            l = list()
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    l.append(self.__parse_element(node)[-1][-1])
            return VARIABLE, (name, frozenset(l))
        elif type in DICT_TYPE:
            l = list()
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    l.append(self.__parse_element(node)[-1][-1])
            return VARIABLE, (name, dict(l))
        elif type in NONE_TYPE:
            return VARIABLE, (name, None)
        elif type in UNSUPPORTED_TYPE:
            return VARIABLE, (name, value)
        elif type in COMMAND_TYPE:
            d = dict()
            # should only be one child node, since we allow only 1 kwargs-dict
            # per command
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE:
                    d = self.__parse_element(node)[-1][-1]
            # TODO: test if all keys are strings
            return COMMAND, (value, d)
        raise DecodingError("Unknown type: %s" % str(type))


    def __get(self, element, what):
        """Return the 'what' of the element or throw exception if no name given."""
        if element.hasAttribute(what):
            return element.getAttribute(what)
        elif element.hasChildNodes():
            for node in element.childNodes:
                if node.nodeType == Node.ELEMENT_NODE and node.nodeName == what:
                    content = ""
                    for child in node.childNodes:
                        if child.nodeType == Node.TEXT_NODE:
                            content += child.nodeValue
                    return content

        return None

class TobiXmlDecoder(XmlDecoder):
    """TobiXmlDecoder.

    Decode packets in TOBI format.

    """

    def __init__(self):
        XmlDecoder.__init__(self)

    def decode_packet(self, packet):
        """Parse the XML string and return a BciSignal.

        :param packet: Packet in TOBO format
        :returns: decoded packet
        :raises: A DecodingError is raised when the parsing of the packet failed.
        """
        dom = None
        try:
            dom = minidom.parseString(packet)
        except:
            raise DecodingError("Not XML at all! (%s)" % str(packet))

        # the root element name will be "messagec" for TOBI interface C packets,
        # if it is anything else, pass it on to the normal pyff decoder
        if dom.documentElement.nodeName == "messagec":
            return self.__decode_tobiic_packet(packet)
        return XmlDecoder.decode_packet(self, packet)

    def __decode_tobiic_packet(self, data):
        l = []    # for the variables
        c = []    # for the commands
        t = None  # for the type

        # deserialize the packet
        icmessage = pylibtobiic.ICMessage()
        icsr = pylibtobiic.ICSerializer(icmessage, True)
        icsr.Deserialize(data)

        # now extract the data from icmessage
        # go through all the classifiers...
        for classifier_name in icmessage.classifiers.map.keys():
            classifier_data = icmessage.classifiers.map[classifier_name]
            print "[TOBI-IC] %s" % classifier_name
            # and all the classes inside the classifier...
            values = []
            for class_name in classifier_data.classes.map.keys():
                class_data = classifier_data.classes.map[class_name]
                print "[TOBI-IC] %s/%s: %.3f" % (classifier_name, class_name, class_data.GetValue())
                # is this the correct way to pass the data value on to pyff??
                values.append(class_data.GetValue())
            l.append((u'cl_output', values))
            break

        t = CONTROL_SIGNAL
        return BciSignal(dict(l), c, t)

class XmlEncoder(object):
    """Generates an XML string from a BciSignal object.

    Usage::

        enc = XmlEncoder()
        try:
            xml = enc.encode_packet(bcisignal)
        except EncodingError:
            ...

    """

    def __init__(self):
        self.logger = logging.getLogger("XmlEncoder")

    def encode_packet(self, signal):
        """Generates an XML packet from a BciSignal object.

        :param signal: Signal
        :type signal: BciSignal
        :raises: An EncodingError is raised if the encoding failed.
        """

        dom = minidom.Document()
        root = dom.createElement(XML_ROOT)
        root.setAttribute(VERSION, CURRENT_VERSION)
        dom.appendChild(root)

        # Write the type
        if signal.type not in [CONTROL_SIGNAL, INTERACTION_SIGNAL, REPLY_SIGNAL]:
            raise EncodingError("Unknown signal type: %s" % str(signal.type))
        root2 = dom.createElement(signal.type)
        root.appendChild(root2)

        # Write the commands
        # each element of the command list is a tuple (command, **kwargs)
        for command, args in signal.commands:
            cmd = dom.createElement(COMMAND_TYPE[0])
            cmd.setAttribute(VALUE, str(command))
            if args:
                self.__write_element(None, args, dom, cmd)
            root2.appendChild(cmd)

        # Write the data
        for d in signal.data:
            try:
                self.__write_element(d, signal.data[d], dom, root2)
            except EncodingError, e:
                # Ignore elements which are unkknown, just print a warning
                self.logger.warning("Unable to write element (%s)" % str(e))
        return dom.toxml('utf-8')


    def __get_type(self, value):
        if isinstance(value, bool):
            type = BOOLEAN_TYPE
        elif isinstance(value, int):
            type = INTEGER_TYPE
        elif isinstance(value, float):
            type = FLOAT_TYPE
        elif isinstance(value, long):
            type = LONG_TYPE
        elif isinstance(value, complex):
            type = COMPLEX_TYPE
        elif isinstance(value, str):
            type = STRING_TYPE
        elif isinstance(value, unicode):
            type = UNICODE_TYPE
        elif isinstance(value, list):
            type = LIST_TYPE
        elif isinstance(value, tuple):
            type = TUPLE_TYPE
        elif isinstance(value, set):
            type = SET_TYPE
        elif isinstance(value, frozenset):
            type = FROZENSET_TYPE
        elif isinstance(value, dict):
            type = DICT_TYPE
        elif value == None:
            type = NONE_TYPE
        else:
            type = UNSUPPORTED_TYPE
        return type


    def __write_element(self, name, value, dom, root):
        type = self.__get_type(value)

        e = dom.createElement(type[0])
        if name:
            e.setAttribute(NAME, name)
        if type in (LIST_TYPE, TUPLE_TYPE, SET_TYPE, FROZENSET_TYPE):
            for v in value:
                #
                # FIXME: does break unsupported types somehow...
                #
                self.__write_element(None, v, dom, e)
        elif type == DICT_TYPE:
            for i in value.items():
                # i is a tuple (key, value)
                # ok we store each key-value pair as a tuple -- now we have to
                # make sure the value isn't unsupported, or surprising results
                # will happen...
                if self.__get_type(i[1]) != UNSUPPORTED_TYPE:
                    self.__write_element(None, i, dom, e)
        elif value != None:
            e.setAttribute(VALUE, unicode(value))
        root.appendChild(e)


class JsonDecoder(object):
    """Decode JSON strings into BciSignal objects."""

    def __init__(self):
        self.logger = logging.getLogger('JsonDecoder')


    def decode_packet(self, signal):
        """Decode JSON strings into a `BciSignal` object.

        Paramters
        ---------
        signal : str
            a string formatted as valid JSON

        Returns
        -------
        sig : BciSignal
            a BciSignal object

        Raises
        ------
        DecodingError : if the decoder is unable to parse the JSON.

        """
        try:
            signaldict = json.loads(signal)
        except ValueError:
            self.logger.error('Unable to parse JSON:')
            self.logger.error(signal)
            raise DecodingError()
        data = signaldict['data']
        commands = signaldict['commands']
        type = signaldict['type']
        if type not in [INTERACTION_SIGNAL, CONTROL_SIGNAL, REPLY_SIGNAL]:
            raise DecodingError("Signal type is %s is not supported" % type)
        return BciSignal(data, commands, type)


# TODO: this really does not belong into this module. We have three
# De/Encoders now, we should also have a base class or eliminate the
# other two after a grace period of testing
class JsonEncoder(object):
    """Encode BciSignal objects into JSON."""

    def __init__(self):
        self.logger = logging.getLogger('JsonEncoder')

    def strip(self, bcisignal):
        """Strip the items we cannot convert.

        This method strips off the items from the BciSignal which cannot
        be converted into JSON (e.g. objects)

        Parameters
        ----------
        bcisignal : BciSignal
            the BciSignal object to strip

        Returns
        -------
        bcisignal : BciSignal
            the stripped BciSignal object

        """
        d2 = dict()
        for k, v in bcisignal.data.iteritems():
            try:
                json.dumps((k, v))
            except:
                self.logger.warning("Unable to convert %s to JSON, ignoring it." % (str((k, v))))
            else:
                d2[k] = v
        c2 = bcisignal.commands
        t2 = bcisignal.type
        return BciSignal(d2, c2, t2)

    def encode_packet(self, bcisignal):
        """Encode BciSignal objects into JSON.

        Parameters
        ----------
        bcisignal : BciSignal
            a BciSignal object

        Returns
        -------
        sig : str
            a JSON formatted string.

        """
        bcisignal_stripped = self.strip(bcisignal)
        signaldict = dict()
        signaldict['data'] = bcisignal_stripped.data
        signaldict['commands'] = bcisignal_stripped.commands
        signaldict['type'] = bcisignal_stripped.type
        if signaldict['type'] not in [INTERACTION_SIGNAL, CONTROL_SIGNAL, REPLY_SIGNAL]:
            raise EncodingError("Signal type is %s is not supported" % signaldict['type'])
        return json.dumps(signaldict)


class BciSignal(object):
    """Represents a signal from the BCI network.

    A BciSignal object can be translated to XML and vice-versa.

    """

    def __init__(self, data, commands, type):
        """
        Initialize a BciSignal object.

        :param data: variables or None
        :type data: dict
        :param commands: tuples (commandname (str), dictionary (kwargs)) or None
        :type commands: list
        :param type: `CONTROL_` or `INTERACTION_SIGNAL`

        """
        # if data or commands == None, convert to empty lists
        if not data:
            data = {}
        if not commands:
            commands = []
        # TODO: check if data, commadns, and type are valid
        self.type = type
        self.data = data
        self.commands = commands

    def __str__(self):
        return 'Type: %s\nData: %s\nCommands: %s\n' % (self.type, self.data, self.commands)


class Error(Exception):
    """Our own exception type."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class EncodingError(Error):
    """Something message cound not be encoded."""
    pass

class DecodingError(Error):
    """Message could not be decoded."""
    pass


def main():
#    if len(sys.argv) < 2:
#        print 'usage: %s infile.xml' % sys.argv[0]
#        sys.exit(-1)
#
#    file = open(sys.argv[1], "r")
#    packet = file.read()
#    file.close()
#    print packet
#    xmldec = XmlDecoder()
#
#    type, data = xmldec.decode_packet(packet)

    d = {"boolean" : True,
         "integer" : 1,
         "float" : 0.69,
         "long" : 1,
         "complex" : 1+0j,
         "string" : "foo",
         "list" : [1, 2, 3, 4, 5, 6],
         "llist" : [[1], [[1],2], [[[1],[2]],[3]]],
         "tuple" : (1, 2, 3, 4, 5, 6),
         "ttuple" : ((1), ((1),2), (((1),(2)),(3))),
         "set" : set([1,2,3]),
         "frozenset" : frozenset([1,2,3,4,5]),
         "dict" : {"foo" : 1, "bar" : 2, "baz" : 3},
         "ddict" : {"key" : "value", "d-in-" : {"foo" : 1, "bar" : 2, "baz" : 3}}
         }
    #d = dict()
    t = "interaction-signal"
    c = [("start", {"foo" : 1}), ("stop", {1 : 2, "l" : [1,2,3]}), ("init", dict())]

    signal = BciSignal(d, c, t)

    encoder = XmlEncoder()
    xml = encoder.encode_packet(signal)
    print xml

    decoder = XmlDecoder()
    signal2 = decoder.decode_packet(xml)
    d2 = signal2.data

    print "*** Elements of the original dictionary:"
    for i in d.items():
        print i

    print "*** Elements of the second dictionary:"
    for i in d2.items():
        print i

    print d == d2
    print signal
    print signal2

    print '***'

    # the following types are not supported by JSON
    d.pop('set')
    d.pop('frozenset')
    d.pop('complex')
    d.pop('tuple')
    d.pop('ttuple')

    encoder = JsonEncoder()
    xml = encoder.encode_packet(signal)
    print xml

    decoder = JsonDecoder()
    signal2 = decoder.decode_packet(xml)
    d2 = signal2.data

    print "*** Elements of the original dictionary:"
    for i in d.items():
        print i

    print "*** Elements of the second dictionary:"
    for i in d2.items():
        print i

    print d == d2
    print signal
    print signal2


if __name__ == "__main__":
    #from timeit import Timer
    #t = Timer("main()")
    #print t.timeit(10)/10

    #main()

    import profile
    import pstats
#    profile.run("main()", "stats")
#    p = pstats.Stats("stats")
#    p.sort_stats("cumulative").print_stats(15)

    main()
