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

from time import sleep
from datetime import datetime, timedelta
import collections, logging, itertools, random

import VisionEgg

from lib.vision_egg.util.frame_counter import FrameCounter

_refresh_rate = VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ
_frame_duration = 1. / _refresh_rate

def _frames(time):
    return int(round(float(time) * _refresh_rate))

def _is_seq(l):
    return isinstance(l, collections.Sequence)

class StimulusTime(object):
    def __init__(self, time, vsync=True):
        self._vsync = vsync
        self._frames = None
        self.set(time)

    def set(self, time):
        self._adapted = self._time = time
        if self:
            self._frames = _frames(self._time)
            if self._vsync:
                self._adapted = round(self._frames * _frame_duration, 6)

    @property
    def time(self):
        return timedelta(seconds=self._adapted)

    @property
    def original(self):
        return self._time

    @property
    def adapted(self):
        return self._adapted

    @property
    def frames(self):
        return self._frames

    def __call__(self, frames):
        return self.frames if frames else self.time

    def __nonzero__(self):
        return self._time is not None

class RandomStimulusTime(StimulusTime):
    def __init__(self, interval, *a, **kw):
        self._interval = interval
        StimulusTime.__init__(self, 0, *a, **kw)

    def _resample(self):
        self.set(random.uniform(*self._interval))

    @property
    def original(self):
        return 'random(%s, %s)' % tuple(self._interval)

    @property
    def adapted(self):
        return self.original

    def __call__(self, frames):
        self._resample()
        return StimulusTime.__call__(self, frames)

def _stimulus_time(time, vsync):
    typ = lambda t: RandomStimulusTime if _is_seq(t) else StimulusTime
    return typ(time)(time, vsync=vsync)

class StimulusPainter(object):
    """ Painter for a series of stimuli. """
    def __init__(self, prepare, wait, view, flag, wait_style_fixed=False,
                 print_frames=False, suspendable=True, pre_stimulus=None,
                 frame_transition=False, vsync=True):
        self._prepare_func = prepare
        self._wait_times = itertools.cycle(wait)
        self._view = view
        self._flag = flag
        self._wait_style_fixed = wait_style_fixed
        self._print_frames = print_frames
        self._suspendable = suspendable
        self._pre_stimulus = pre_stimulus
        self._frame_transition = frame_transition
        self._vsync = vsync
        self._logger = logging.getLogger('StimulusPainter')
        self._frame_counter = FrameCounter(self._flag)
        self._suspended_time = timedelta()
        self._wait = self._frame_wait if frame_transition else self._time_wait
        self._online_times = []

    def run(self):
        if self._print_frames or self._frame_transition:
            self._frame_counter.start()
        if self._prepare():
            self._last_start = datetime.now()
            self._frame_counter.lock()
            self._present()
            while self._prepare():
                self._wait()
                self._present()
            if self._flag:
                self._wait()
        if self._print_frames:
            self._logger.debug('Frames rendered during last sequence: %d' %
                               self._frame_counter.frame)

    def _frame_wait(self):
        next_interval = self._next_duration
        while self._flag and self._frame_counter.last_interval < next_interval:
            self._frame_counter.sync()
        if self._print_frames:
            self._logger.debug('Frames after waiting: %d' %
                               self._frame_counter.last_interval)

    def _time_wait(self):
        next_start = self._last_start + self._next_duration
        while next_start - datetime.now() > timedelta():
            pass
        self._last_start = (next_start if self._wait_style_fixed else
                            datetime.now())
        if self._print_frames:
            self._logger.debug('Frames after waiting: %d' %
                               self._frame_counter.last_interval)

    def _prepare(self):
        if self._flag:
            if self._suspendable and self._flag.suspended:
                suspend_start = datetime.now()
                self._flag.wait()
                self._suspended_time = datetime.now() - suspend_start
            return self._do_prepare()

    def _present(self):
        if self._print_frames:
            self._logger.debug('Frames before stimulus change: %d' %
                               self._frame_counter.last_interval)
        if self._pre_stimulus is not None:
            self._pre_stimulus()
        self._frame_counter.lock()
        self._view.update()

    @property
    def _next_duration(self):
        try:
            nxt = self._online_times.pop(0) or self._wait_times.next()
        except StopIteration:
            raise Exception('No specified stimulus times available!')
        return nxt(self._frame_transition) + self._suspended

    @property
    def _suspended(self):
        t = self._suspended_time
        self._suspended_time = timedelta()
        return _frames(t.total_seconds()) if self._frame_transition else t

class StimulusSequence(StimulusPainter):
    def _do_prepare(self):
        self._online_times.append(_stimulus_time(None, self._vsync))
        return self._prepare_func()

class StimulusIterator(StimulusPainter):
    """ Painter using an iterator. """
    def __init__(self, *a, **kw):
        StimulusPainter.__init__(self, *a, **kw)

    def _do_prepare(self):
        try:
            nxt = self._prepare_func.next()
            self._online_times.append(_stimulus_time(nxt, self._vsync))
            return True
        except StopIteration:
            return False

class StimulusSequenceFactory(object):
    """ This class instantiates StimulusPainter in create().
    Depending on whether the supplied prepare object is a function or a
    generator, StimulusSequence or StimulusIterator are used,
    respectively.
    """
    def __init__(self, view, flag, print_frames=False, vsync_times=False,
                 frame_transition=False):
        self._view = view
        self._flag = flag
        self._print_frames = print_frames
        self._vsync_times = vsync_times
        self._frame_transition = frame_transition
        self._logger = logging.getLogger('StimulusSequenceFactory')

    def create(self, prepare, times=None, wait_style_fixed=True,
               suspendable=True, pre_stimulus=None):
        """ Create a StimulusPainter using the preparation object
        prepare, with given presentation times and wait style.
        If suspendable is True, the sequence halts when on_pause is
        pressed.
        Global parameters from pyff are used as given in __init__.
        """
        if times is None:
            times = []
        else:
            times = self._times(times)
            self._debug_times(times)
        typ = (StimulusIterator if hasattr(prepare, '__iter__') else
               StimulusSequence)
        return typ(prepare, times, self._view, self._flag,
                   wait_style_fixed=wait_style_fixed,
                   print_frames=self._print_frames, suspendable=suspendable,
                   pre_stimulus=pre_stimulus,
                   frame_transition=self._frame_transition,
                   vsync=self._vsync_times)

    def _times(self, times):
        if not _is_seq(times):
            times = [times]
        return [_stimulus_time(t, vsync=self._vsync_times) for t in times]

    def _debug_times(self, times):
        original = [t.original for t in times]
        adapted = [t.adapted for t in times]
        frames = [t.frames for t in times]
        if self._frame_transition:
            text = ('Adapted stimulus times %s to %s frames (%s)' %
                    (original, frames, adapted))
            self._logger.debug(text)
        elif self._vsync_times:
            text = 'Adapted stimulus times %s to %s' % (original, adapted)
            self._logger.debug(text)
