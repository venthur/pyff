# eyetracker.py - 
# Copyright (C) 2009  Bastian Venthur
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


import socket
import threading


class EyeTracker(object):
    
    def __init__(self):
        self.thread = None
        self.stop = True
    
    def start(self):
        self.thread = threading.Thread(target=self.listen)
        self.stop = False
        self.thread.start()
        
    def stop(self):
        self.stop = True
        self.thread.join(10)
        self.thread = None
    
    def listen(self): 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 1111))
        sock.listen(1)
        conn, addr = sock.accept()
        while not self.stop:
            data = conn.recv(1024)
            print str(data)
            if data == "REG:EYE":
                print "Sennding ACK...",
                conn.send("ACK")
                print "done."
        conn.close()


if __name__ == "__main__":
    et = EyeTracker()
    et.start()
    # read something
    et.stop()
