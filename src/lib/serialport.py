# pyffserial.py -
# Copyright (C) 2010 - 2014  Chris Hausler, Bastian Venthur
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


#
# This file can be imported to allow reading and writing from a serial port<
#
# other properties of the port such as Blockin, parity, byte size etc can also
# be set if needed
#
# Requires pySerial - http://pyserial.sourceforge.net/ There are also some
# useful test python files on the sourceforge site for testing the serial port
# functionality


import serial
from threading import Timer


class SerialPort(object):

    def __init__(self, port, baudrate=57600):
        """Open the serial port.

        Parameters
        ----------
        port : int
        baudrate : int

        """
        self.port = serial.Serial(port=port, baudrate=baudrate)
        self.trigger_reset_time = 0.01
        self.reset_timer = Timer(0, None)


    def send(self, data, reset=True):
        """Send data to serial port.

        Parameters
        ----------
        data : bytevalue

        """
        if reset == True:
            self.reset_timer.cancel()
        self.port.write(chr(data))
        if reset == True:
            self.reset_timer = Timer(self.trigger_reset_time, self.send, (0, False))
            self.reset_timer.start()

    def close(self):
        self.port.close()


def scan():
    """Scan for available ports.

    Returns
    -------

    ports : list of (int, str)
        the elements of the tuples are the number and the name of the
        port.

    """
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.portstr))
            s.close()
        except serial.SerialException:
            pass
    return available

