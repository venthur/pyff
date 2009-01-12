# Lesson03 - Working with data send by control- and interaction signals
# Copyright (C) 2007-2009  Bastian Venthur
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


from FeedbackBase.Feedback import Feedback

import time

class Lesson03(Feedback):
    
    def on_init(self):
        print "Feedback successfully loaded."
        self.quitting, self.quit = False, False
        self.pause = False
    
    def on_quit(self):
        self.quitting = True
        # Make sure we don't return on_quit until the main_loop (which runs in
        # a different thread!) quit.
        print "Waiting for main loop to quit."
        while not self.quit:
            pass
        # Now the main loop quit and we can safely return

    def on_play(self):
        # Start the main loop. Note that on_play runs in a different thread than
        # all the other Feedback methods, and so does the main loop.
        self.quitting, self.quit = False, False
        self.main_loop()
        
    def on_pause(self):
        self.pause = not self.pause
        
    def main_loop(self):
        i = 0
        while 1:
            time.sleep(0.5)
            if self.pause:
                print "Feedback Paused."
                continue
            elif self.quitting:
                print "Leaving main loop."
                break
            print self._data
            
        print "Left main loop."
        self.quit = True