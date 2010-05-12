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
TIMEOUT = 0

def send_serial(data):
    """ Send data to serial port """
    s = serial.serial_for_url(PORT, timeout=TIMEOUT)
    s.write(data)
    s.close()
    
def read_serial(numBytes=1):
    """ Read a given number of Bytes from the serial port. default is 1"""
    s = serial.serial_for_url(PORT, timeout=TIMEOUT)
    res = s.read(numBytes)
    s.close()
    return res


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