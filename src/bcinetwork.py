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
        