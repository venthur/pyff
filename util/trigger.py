__copyright__ = """ Copyright (c) 2010 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

"""

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

def symbol_trigger(symbol, target, alphabet, base=TRIG_LETTER):
    value = base + alphabet.index(symbol)
    if symbol == target:
        value += TRIG_TARGET_ADD
    return value

def eeg_trigger(symbol, alphabet):
    return symbol_trigger(symbol, None, alphabet, base=TRIG_EEG)
