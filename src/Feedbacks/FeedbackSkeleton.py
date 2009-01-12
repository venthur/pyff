# FeedbackSkeleton.py -
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


import time

from FeedbackBase.Feedback import Feedback


class FeedbackSkeleton(Feedback):
    
################################################################################
# From Feedback Base Class
################################################################################
    def on_init(self):
        self.stopping, self.stopped, self.paused = False, False, False
    
    def on_play(self):
        self.main_loop()
    
    def on_pause(self):
        self.paused = not self.paused

    def on_quit(self):
        self.stopping = True
        while not self.stopped:
            pass
    
    def on_interaction_event(self, data):
        pass

    def on_control_event(self, data):
        pass
################################################################################
# /From Feedback Base Class
################################################################################

    def main_loop(self):
        while not self.stopping:
            time.sleep(1)
            if self.paused:
                self.logger.debug("Pause.")
                continue
            elif self.stopping:
                self.logger.debug("Stopping.")
                break
            #
            # Here goes the actual main loop code
            #
            self.logger.debug("Main-Looping.")
        self.stopped = True
    

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    fb = FeedbackSkeleton()
    fb.on_init()
    fb.on_play()
