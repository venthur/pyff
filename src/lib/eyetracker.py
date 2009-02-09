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


#['17\\48\\56\\421', '607', '323', 'F', 'F', '160\r\n']
#17\48\56\437:607:322:F:F:180
#
#['17\\48\\56\\437', '607', '322', 'F', 'F', '180\r\n']
#17\48\56\453:608:322:F:F:200
#
#['17\\48\\56\\453', '608', '322', 'F', 'F', '200\r\n']
#17\48\56\468:609:321:F:F:220
#
#['17\\48\\56\\468', '609', '321', 'F', 'F', '220\r\n']
#17\48\56\500:609:321:F:F:240
#
#['17\\48\\56\\500', '609', '321', 'F', 'F', '240\r\n']
#CHE:EYE
#['CHE', 'EYE']


class EyeTracker(object):
    
    def __init__(self):
        self.thread = None
        self.stopping = True
    
    def start(self):
        self.thread = threading.Thread(target=self.listen)
        self.stopping = False
        self.thread.start()
        
    def stop(self):
        self.stopping = True
        self.thread.join(10)
        self.thread = None
    
    def listen(self): 
        print "Preparing socket...",
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 1111))
        sock.listen(1)
        print "done."
        while not self.stopping:
            print "Waiting for incoming connection...",
            conn, addr = sock.accept()
            print "done."
            while not self.stopping:
                # FIXME: we should probably loop recv until we got one full
                # packet
                data = conn.recv(4096)
                print str(data)
                if data == "REG:EYE":
                    print "Sennding ACK...",
                    conn.send("ACK")
                    print "done."
                if not data:
                    print "Received empty packet, closing connection."
                    break
            print "Closing socket...",
            conn.close()
            print "done."

    def parse_data(self, data):
        self.timestamp = 0
        self.x = 0
        self.y = 0
        self.duration = 0


if __name__ == "__main__":
    import time
    et = EyeTracker()
    et.start()
    time.sleep(60)
    # read something
    et.stop()
