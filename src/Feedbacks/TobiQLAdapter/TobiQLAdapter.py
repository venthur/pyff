
from xml.dom.minidom import Document
import socket
import time

from FeedbackBase.MainloopFeedback import MainloopFeedback

LEFT = -1.
RIGHT = 1.
NONE = 0.

class TobiQLAdapter(MainloopFeedback):
    
    def init(self):
        self.server_address = ("127.0.0.1", 10001)
        self.left_signal = "l"
        self.right_signal = "r"
        
        # control_signal = bias + gain * control_signal
        self.gain = 1.0
        self.bias = 0.0
        
        # Last selected, value
        self.last = NONE
        
        # current control signal
        self.cs = 0.0

    
    def play_tick(self):
        time.sleep(0.5)
        if self.cs <= LEFT and (self.last == RIGHT or self.last == NONE):
            self.send_signal(self.left_signal)
            self.last = LEFT
        elif self.cs >= RIGHT and (self.last == LEFT or self.last == NONE):
            self.send_signal(self.right_signal)
            self.last = RIGHT
        print "%i \t %f\r" % (self.last, self.cs)

    
    def on_control_event(self, data):
        cs = data["cl_output"]
        self.cs = self.bias + self.gain * cs
        

# The stuff below is taken from the Tobi API client example
    def send_signal(self, signal):
        """Sends the signal to the server, I guess."""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect(self.get_server_address())
        except socket.error, msg:
            self.logger.critical("Error connecting to server (%s)" % str(msg))
            return
        
        request = self.build_request(signal)
        server.send(request)
        
        data = server.recv(1024)
        string = ""
        while len(data):
            string = string + data
            data = server.recv(1024)
        server.close()
        self.logger.debug("Server replied with: %s" % str(string))
 

    def build_request(self, signal):
        """Builds the XML message from the signal."""
        doc = Document()
        e1 = doc.createElement("TOBI_communication");
        e2 = doc.createElement("signal")
        a = doc.createAttribute("Type")
        a.value = str(signal)
        e2.attributes[a.name] = a.value
        e1.appendChild(e2)
        doc.appendChild(e1)
        return doc.toxml()


    def parse_response(self, response):
        """Parses the response or throws an exception."""
        pass
    

    def get_server_address(self):
        """Reads the configuration file and returns the IPendPoint object or
        throws an exception."""
        return self.server_address
