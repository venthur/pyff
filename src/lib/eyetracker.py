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
import logging


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
        self.logger = logging.getLogger("EyeTracker")
        self.logger.debug("Logger initialized.")
        self.thread = None
        self.stopping = True
        self.time_h = None
        self.time_m = None
        self.time_s = None
        self.time_ms = None
        self.x = None
        self.y = None
        self.duration = None
        
    
    def start(self):
        self.thread = threading.Thread(target=self.listen)
        self.stopping = False
        self.thread.start()
        
    def stop(self):
        self.stopping = True
        self.thread.join(1)
        self.thread = None
    
    def listen(self): 
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", 1111))
        sock.listen(1)
        while not self.stopping:
            self.logger.debug("Waiting for incoming connection...")
            conn, addr = sock.accept()
            self.logger.debug("Got connection.")
            while not self.stopping:
                # FIXME: we should probably loop recv until we got one full
                # packet
                data = conn.recv(4096)
                if data.endswith(r"\r\n"):
                    data = data[:-4]
                if data == "REG:EYE":
                    self.logger.debug("Sending ACK...")
                    conn.send("ACK")
                elif self.is_parsable(data):                 
                    self.parse_data(data)
                elif not data:
                    self.logger.debug("Received empty packet, closing connection.")
                    break
                else:
                    self.logger.warning("Hmm got data and don't know what to do with it: %s" % str(data))
            self.logger.debug("Closing connection.")
            conn.close()
        self.logger.debug("Closing socket.")
        sock.close()

    def parse_data(self, data):
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
        time, x, y, crap1, crap2, duration = data.split(":")
        h, m, s, ms = time.split("\\")
        
        self.time_h = int(h)
        self.time_m = int(m)
        self.time_s = int(s)
        self.time_ms = int(ms)
        self.x = int(x)
        self.y = int(y)
        self.duration = int(duration)
        
    def is_parsable(self, data):
        return data.count(":") == 5
        


if __name__ == "__main__":
    import time
    et = EyeTracker()
    et.start()
    time.sleep(60)
    # read something
    et.stop()
