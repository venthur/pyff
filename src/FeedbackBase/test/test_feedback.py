# test_feedback.py -
# Copyright (C) 2008-2011  Bastian Venthur
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

from FeedbackBase.Feedback import Feedback


class FeedbackTestCase(unittest.TestCase):

    def testFeedbackInitWithoutArguments(self):
        """Feedback should instantiate without arguments."""
        try:
            fb = Feedback()
        except:
            self.fail()

    def testFeedbackInitWithArguments(self):
        """Feedback should instantiate with one argument."""
        try:
            fb = Feedback(None)
        except:
            self.fail()

    def testFeedbackCallbacks(self):
        """_on_play, _pause, _stop and _quit should work."""
        fb = Feedback()
        try:
            fb._on_play()
            fb._on_pause()
            fb._on_stop()
            fb._on_quit()
        except:
            self.fail()

def suite():
    testSuite = unittest.makeSuite(FeedbacksTestCase)
    return testSuite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())

if __name__ == "__main__":
    main()
