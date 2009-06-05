# test_iothread.py -
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


import unittest

from processing import Pipe, Event

from lib.iothread import IOThread


class IOThreadTestCase(unittest.TestCase):
    
    def _process_object(self, obj):
        self.received.append(obj)
        self.event.set()
    
    def setUp(self):
        self.myEnd, otherEnd = Pipe()
        self.received = []
        IOThread.process_object = self._process_object
        self.ioThread = IOThread(otherEnd, 0)
        self.event = Event() 
        self.ioThread.start()
        
    def tearDown(self):
        self.ioThread.stop()
        self.ioThread.join()

    def test_send_recv(self):
        """Testing sending data to thread."""
        self.myEnd.send("foo")
        self.event.wait()
        self.assertEquals(self.received[0], "foo")
        
    def test_send_recv2(self):
        """Testing thread sends data."""
        self.ioThread.send("foo")
        self.assertEquals(self.myEnd.recv(), "foo")
        
    def test_join_before_start(self):
        """IOThread should join correctly even if not started."""
        try:
            self.ioThread.join(0)
        except:
            self.assert_(False)
            
        
        
#suite = unittest.makeSuite(IOThreadTestCase)
def suite():
    testSuite = unittest.makeSuite(IOThreadTestCase)
    return testSuite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
if __name__ == "__main__":
    main()
    