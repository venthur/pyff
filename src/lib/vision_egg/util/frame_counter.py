__copyright__ = """ Copyright (c) 2010-2011 Torsten Schmits

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

import logging
import threading

import pygame

class FrameCounter(threading.Thread):
    """ Runs a thread that calls flip() repeatedly, which waits for
    vsync and thus indicates real display redraws. """
    def __init__(self, flag):
        threading.Thread.__init__(self)
        self._flag = flag
        self.frame = 0
        self._locked_frame = 0
        
    def run(self):
        try:
            while self._flag:
                self.step()
        except pygame.error as e:
            logging.getLogger('FrameCounter').error(unicode(e))

    def step(self):
        self.sync()
        self.frame += 1

    def sync(self):
        pygame.display.flip()

    def lock(self):
        self._locked_frame = self.frame

    @property
    def last_interval(self):
        return self.frame - self._locked_frame
