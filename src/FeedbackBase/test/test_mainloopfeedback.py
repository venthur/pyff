# test_mainloopfeedback.py -
# Copyright (C) 2008-2009  Bastian Venthur
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
from threading import Thread

from FeedbackBase.MainloopFeedback import MainloopFeedback


class MainloopFeedbackTestCase(unittest.TestCase):
    
    def setUp(self):
        self.fb = MainloopFeedback()
        self.init()
    
    def tearDown(self):
        self.quit(1)
    
    def testPlayQuit(self):
        """Mainloop Feedback should handle: init + play + quit."""
        self.play()
        self.assertTrue(self.quit())
        
    def testQuit(self):
        """Mainloop Feedback should handle: init + quit."""
        self.assertTrue(self.quit())
        
    def testQuitQuit(self):
        """Mainloop Feedback should handle: init + quit + quit."""
        self.assertTrue(self.quit())
        self.assertTrue(self.quit())

    def testInitInit(self):
        """Mainloop Feedback should handle: init + init."""
        self.assertTrue(self.init())
        self.assertTrue(self.init())

    def testPlayPauseStopQuit(self):
        """Mainloop Feedback should handle: init + play + pause + stop + quit."""
        self.play()
        self.pause()
        self.stop()
        self.assertTrue(self.quit())
        
    def testPlayPausePauseStopQuit(self):
        """Mainloop Feedback should handle: init + play + pause + pause + stop + quit."""
        self.play()
        self.pause()
        self.pause()
        self.stop()
        self.assertTrue(self.quit())


    def init(self, timeout=None):
        return self.call_async(self.fb.on_init, timeout)

    def play(self, timeout=-1):
        return self.call_async(self.fb.on_play, timeout)
        
    def pause(self, timeout=None):
        return self.call_async(self.fb.on_pause, timeout)

    def stop(self, timeout=None):
        return self.call_async(self.fb.on_stop, timeout)

    def quit(self, timeout=None):
        return self.call_async(self.fb.on_quit, timeout)
    
    def call_async(self, mytarget, timeout=None):
        """Call the method in a seperate thread and join.
        
        If a timeout is given join waits timeout seconds otherwise it waits
        until the thread quits itself.
        
        If the timeout is -1 the method returns without joining.
        """
        thread = Thread(target=mytarget)
        thread.start()
        if timeout == -1:
            return True
        thread.join(timeout)
        return not thread.isAlive()


def suite():
    testSuite = unittest.makeSuite(MainloopFeedbackTestCase)
    return testSuite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
if __name__ == "__main__":
    main()