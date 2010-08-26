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
import datetime

def time():
    """ Return microsecond-accurate time since last midnight. 
    Workaround for time() having only 10ms accuracy when VE is running.
    """
    n = datetime.datetime.now()
    return 60. * (60 * n.hour + n.minute) + n.second + n.microsecond / 1000000.

class StimulusPainter(object):
    """ Painter for a series of stimuli. """
    def __init__(self, prepare, wait, view, flag, wait_style_fixed=False):
        self._prepare_func = prepare
        self._wait_time = wait
        self._view = view
        self._flag = flag
        self._wait_style_fixed = wait_style_fixed
        
    def run(self):
        if self._prepare():
            self._last_start = time()
            self._present()
            while self._prepare():
                self._wait()
                self._present()
            self._wait()

    def _wait(self):
        wait_time = self._last_start - time() + self._wait_time
        sleep(wait_time)
        if self._wait_style_fixed:
            self._last_start += self._wait_time
        else:
            self._last_start = time()

    def _prepare(self):
        if self._flag:
            return self._do_prepare()

    def _present(self):
        print self._last_start
        self._view.present_frames(1)

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
    def __init__(self, flag):
        self._flag = flag

    def set_view(self, view):
        self._view = view
        
    def create(self, prepare, presentation_time, wait_style_fixed):
        #real_time = presentation_time - self._frame_duration
        real_time = presentation_time
        typ = StimulusIterator if hasattr(prepare, '__iter__') else \
               StimulusSequence
        return typ(prepare, real_time, self._view, self._flag, wait_style_fixed)
