# test_eyetracker.py -
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
import socket
import time

from lib.eyetracker import EyeTracker


class EyeTrackerTestCase(unittest.TestCase):
    
    def setUp(self):
        self.et = EyeTracker()
        self.et.start()
        self.etserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(0.1)
        try:
            self.etserver.connect(("", 1111))
        except:
            # We pretend everything is working when no eyetracker is available
            # for testing purposes
            self.etserver = None
        
    def tearDown(self):
        self.et.stop()
        if self.etserver is None:
            return
        self.etserver.close()
    
    def testParser(self):
        """EyeTracker should correctly parse valid data from the eyetracker."""
        if self.etserver is None:
            return
        self.etserver.send(r"17\48\56\437:607:322:F:F:180\r\n")
        time.sleep(0.1)
        self.assertEqual(self.et.time_h, 17)
        self.assertEqual(self.et.time_m, 48)
        self.assertEqual(self.et.time_s, 56)
        self.assertEqual(self.et.time_ms, 437)
        self.assertEqual(self.et.x, 607)
        self.assertEqual(self.et.y, 322)
        self.assertEqual(self.et.duration, 180)
        
        
        
#suite = unittest.makeSuite(BcixmlTestCase)
def suite():
    testSuite = unittest.makeSuite(EyeTrackerTestCase)
    return testSuite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
if __name__ == "__main__":
    main()
    