#
# This file can be imported to allow reading and writing from a serial port<
#
# other properties of the port such as Blockin, parity, byte size etc can also be set
# if needed
#
# Requires pySerial - http://pyserial.sourceforge.net/
# There are also some useful test python files on the sourceforge site for testing the 
# serial port functionality

# author: Chris Hausler
# 13.4.10

import serial

PORT = 0
TIMEOUT = 1
BYTESIZE = 8
BAUDRATE = 2400
PARITY = 'N'
STOPBITS = 2


class pyffserial:
    
    def __init__(self, _port=PORT, _timeout=TIMEOUT, _bytesize=BYTESIZE, 
                 _baudrate = BAUDRATE, _parity=PARITY, _stopbits = STOPBITS):
        """init. can set all of the serial port parameters here otherwise defaults used """
        self.s_port = serial.Serial(port=_port, timeout=_timeout, 
                                            bytesize=_bytesize, baudrate=_baudrate, 
                                            parity=_parity, stopbits=_stopbits)
        
    def send_serial(self,data):
        """ Send data to serial port """
        self.s_port.write(chr(data))
        
        
    def read_serial(self,numBytes=1):
        """ Read a given number of Bytes from the serial port. default is 1"""
        res =self.s_port.read()
        return res
    
    def close(self):
        self.s_port.close()
    
def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available
