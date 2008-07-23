#!/usr/bin/env python
# coding: utf8

import bcinetwork
import bcixml

import socket
import asyncore
import threading
import logging
import sys

class FeedbackController(object):
    def __init__(self):
        # Setup my stuff:
        self.logger = logging.getLogger("FeedbackController")
        self.encoder = bcixml.XmlEncoder()
        self.decoder = bcixml.XmlDecoder()
        
        # Listen on the network in a second thread
        Dispatcher(bcinetwork.FC_PORT, self)
        self.networkThread = threading.Thread(target=asyncore.loop, args=())
        self.networkThread.start()
        
        # start my main loop
        print "startet main loop"
        self.main_loop()
    
    def on_signal(self, address, datagram):
        signal = None
        try:
            signal = self.decoder.decode_packet(datagram)
            signal.peeraddr = address
        except bcixml.DecodingError, e:
            # ok, somehow the parsing failed, just drop the packet and print a
            # warning
            self.logger.warning("Parsing of signal failed, ignoring it. (%s)" % str(e))
            return
        # check our signal if it contains anything useful, if not drop it and
        # print a warning
        if signal.type == bcixml.CONTROL_SIGNAL:
            self._handle_cs(signal)
        elif signal.type == bcixml.INTERACTION_SIGNAL:
            self._handle_is(signal)
        else:
            self.logger.warning("Unknown signal type, ignoring it. (%s)" % str(signal.type))

        
    def main_loop(self):
        while True:
            #print "main loop."
            pass


    def _handle_cs(self, signal):
        pass
    
    def _handle_is(self, signal):
        if len(signal.commands) < 1:
            self.logger.warning("Received interaction signal without command, ignoring it.")
            return
        cmd = signal.commands[0]
        # check if this signal is for the FC only (and not for the feedback)
        if cmd == bcixml.CMD_GET_FEEDBACKS:
            ip, port = signal.peeraddr[0], bcinetwork.GUI_PORT
            bcinetw = bcinetwork.BciNetwork(ip, port)
            answer = bcixml.BciSignal({"feedbacks" : ["foo", "bar", "baz", "bratwurst"]}, None, bcixml.INTERACTION_SIGNAL)
            self.logger.debug("Sending %s to %s:%s." % (str(answer), str(ip), str(port)))
            bcinetw.send_signal(answer)
            return
        
        self.feedback._Feedback__on_interaction_event(signal.data)
        if cmd == bcixml.CMD_PLAY:
            self.logger.info("Received PLAY signal")
            self.feedback._Feedback__on_play()
        elif cmd == bcixml.CMD_PAUSE:
            self.logger.info("Received PAUSE signal")
            self.feedback._Feedback__on_pause()
        elif cmd == bcixml.CMD_QUIT:
            self.logger.info("Received QUIT signal")
            self.feedback._Feedback__on_quit()
            # Load the default dummy Feedback
            self.feedback = Feedback(self.pp)
        elif cmd == bcixml.CMD_SEND_INIT:
            self.logger.info("Received SEND_INIT signal")
            # Working with old Feedback!
            self.feedback._Feedback__on_quit()
            self.load_feedback()
            # Proably a new one!
            self.feedback._Feedback__on_init()
            self.feedback._Feedback__on_interaction_event(e.data)
        else:
            self.logger.info("Received generic interaction signal")


class Dispatcher(asyncore.dispatcher):
    def __init__(self, port, feedbackController):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", port))
        #self.handle_read = self.handle_read
        self.feedbackController = feedbackController
        
    def writable(self):
        return False

    def handle_connect(self):
        pass
        
    def handle_read(self):
        datagram = self.recv(bcinetwork.BUFFER_SIZE)
        self.feedbackController.on_signal(self.addr, datagram)    


def start_fc():
    fc = FeedbackController()

def stop_fc():
    pass

if __name__ == '__main__':
    loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format='%(name)-12s %(levelname)-8s %(message)s')
    try:
        start_fc()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Caught keyboard interrupt or system exit; quitting")
        stop_fc()
        sys.exit()
