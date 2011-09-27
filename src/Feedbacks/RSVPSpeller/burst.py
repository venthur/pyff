__copyright__ = """ Copyright (c) 2010-2011 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

"""

from time import sleep

from RSVPSpeller.util.trigger import TRIG_BURST_START, TRIG_BURST_END

class BurstConstraints(object):
    def __init__(self, fix, ask, view, asker, sleep_interval, trigger):
        dummy = lambda: None
        self._clear_symbol = view.clear_center_word
        self._fixation_cross = view.show_fixation_cross if fix else dummy
        self._ask = asker if ask else dummy
        self._sleep_interval = sleep_interval
        self._trigger = trigger

    def __enter__(self):
        self._fixation_cross()
        self._trigger(TRIG_BURST_START, wait=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._clear_symbol()
        self._trigger(TRIG_BURST_END, wait=True)
        self._ask()
        sleep(self._sleep_interval)
        return False
