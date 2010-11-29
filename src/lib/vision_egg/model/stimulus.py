__copyright__ = """ Copyright (c) 2010 Torsten Schmits

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

from time import sleep
import datetime, collections, logging

import pygame

from lib.vision_egg.util.frame_counter import FrameCounter

def time():
    """ Return microsecond-accurate time since last midnight. 
    Workaround for time() having only 10ms accuracy when VE is running.
    """
    n = datetime.datetime.now()
    return 60. * (60 * n.hour + n.minute) + n.second + n.microsecond / 1000000.

class StimulusPainter(object):
    """ Painter for a series of stimuli. """
    def __init__(self, prepare, wait, view, flag, wait_style_fixed=False,
                 print_frames=False):
        self._prepare_func = prepare
        self._wait_time_value = wait
        self._view = view
        self._flag = flag
        self._wait_style_fixed = wait_style_fixed
        self._print_frames = print_frames
        self._wait_time = 0.1
        self._logger = logging.getLogger('StimulusPainter')
        self._frame_counter = FrameCounter(self._flag)

    def _setup_wait_time(self):
        self._individual_wait_times = (isinstance(self._wait_time_value,
                                                 collections.Sequence) and
                                       self._wait_time_value)
        if self._individual_wait_times:
            self._wait_time = iter(self._wait_time_value)
        else:
            self._wait_time = self._wait_time_value
        
    def run(self):
        self._setup_wait_time()
        if self._print_frames:
            self._frame_counter.start()
        if self._prepare():
            self._last_start = time()
            self._frame_counter.lock()
            self._present()
            while self._prepare():
                self._wait()
                self._present()
            self._wait()

    def _wait(self):
        next_wait_time = self._next_wait_time
        wait_time = self._last_start - time() + next_wait_time
        try:
            if wait_time >= 0:
                sleep(wait_time)
        except IOError, e:
            self._logger.error('Encountered "%s" with wait_time of %s'
                               % (e, wait_time))
        if self._wait_style_fixed:
            self._last_start += next_wait_time
        else:
            self._last_start = time()
        if self._print_frames:
            self._logger.debug('Frames after waiting: %d' %
                               self._frame_counter.last_interval)

    def _prepare(self):
        if self._flag:
            return self._do_prepare()

    def _present(self):
        if self._print_frames:
            self._logger.debug('Frames before stimulus change: %d' %
                               self._frame_counter.last_interval)
            self._frame_counter.lock()
        self._view.present_frames(1)

    @property
    def _next_wait_time(self):
        if self._individual_wait_times:
            try:
                return self._wait_time.next()
            except StopIteration:
                self._setup_wait_time()
                return self._wait_time.next()
        else:
            return self._wait_time

class StimulusSequence(StimulusPainter):
    def _do_prepare(self):
        return self._prepare_func()

class StimulusIterator(StimulusPainter):
    """ Painter using an iterator. """
    def _do_prepare(self):
        try:
            self._prepare_func.next()
            return True
        except StopIteration:
            return False

class StimulusSequenceFactory(object):
    def __init__(self, flag, print_frames=False):
        self._flag = flag
        self._print_frames = print_frames

    def set_view(self, view):
        self._view = view
        
    def create(self, prepare, presentation_time, wait_style_fixed):
        #real_time = presentation_time - self._frame_duration
        real_time = presentation_time
        typ = StimulusIterator if hasattr(prepare, '__iter__') else \
               StimulusSequence
        return typ(prepare, real_time, self._view, self._flag,
                   wait_style_fixed=wait_style_fixed,
                   print_frames=self._print_frames)
