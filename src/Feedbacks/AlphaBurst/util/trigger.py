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

import time

TRIG_RUN_START = 252
TRIG_RUN_END = 253
TRIG_COUNTDOWN_START = 200
TRIG_COUNTDOWN_END = 201
TRIG_BURST_START = 105
TRIG_BURST_END = 106
TRIG_LETTER = 31
TRIG_TARGET_ADD = 40
TRIG_COUNTED_OFFSET = 150
TRIG_TARGET_ABSENT_OFFSET = 11
TRIG_TARGET_PRESENT_OFFSET = 21
TRIG_EEG = 131

def add_target_offset_if(value, symbol, target):
    if symbol == target:
        value += TRIG_TARGET_ADD
    return value

def burst_symbol(symbol, target, base=TRIG_LETTER):
    value = base + ord(symbol.lower()) - ord('a')
    return add_target_offset_if(value, symbol, target)

def eeg_symbol(symbol):
    return burst_symbol(symbol, None, base=TRIG_EEG)

class Triggerer(object):
    def __init__(self, nonalpha_trigger, trigger, wait=False):
        self._nonalpha_trigger = dict(nonalpha_trigger)
        self._trigger = trigger
        self._wait = wait
        self._target = ''
        self.symbol('')

    def symbol(self, symbol):
        self._symbol = symbol

    def target(self, target):
        self._target = target

    def __call__(self):
        try:
            if self._symbol.isalpha():
                trigger = self._symbol_trigger()
            else:
                value = self._nonalpha_trigger[self._symbol]
                trigger = add_target_offset_if(value, self._symbol,
                                               self._target)
        except KeyError:
            # redundant symbol
            pass
        else:
            self._trigger(trigger)
            if self._wait:
               time.sleep(0.02)

class BurstTriggerer(Triggerer):
    def _symbol_trigger(self):
        return burst_symbol(self._symbol, self._target)

class EEGTriggerer(Triggerer):
    def __init__(self, nonalpha_trigger, trigger):
        Triggerer.__init__(self, nonalpha_trigger, trigger, wait=True)

    def _symbol_trigger(self):
        return eeg_symbol(self._symbol)
