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

import pygame

__all__ = ['CalibrationInputHandler', 'CopySpellingInputHandler',
           'FreeSpellingInputHandler']

class InputHandler(object):
    def __init__(self, control, triggerer=None):
        self._alphabet = list(control.symbols)
        self._view = control._view
        self._trigger = control._trigger
        self._triggerer = triggerer
        self._symbol = ''

    def start_experiment(self, experiment):
        self._experiment = experiment

    def start_trial(self, trial):
        pass

CalibrationInputHandler = InputHandler

class SpellingInputHandler(InputHandler):
    def __init__(self, control, update_word=False, *a, **kw):
        self._input = ''
        self._delete_symbol = control.delete_symbol
        self._update_word = update_word
        self._allow_keyboard = control.allow_keyboard_input
        InputHandler.__init__(self, control, *a, **kw)

    def keyboard(self, event):
        s = event.unicode
        if (self._allow_keyboard and s in self._alphabet):
            self.eeg_select(self._alphabet.index(s))

    def eeg_select(self, cls):
        if 0 <= cls < len(self._alphabet):
            symbol = self._alphabet[cls]
            if symbol == self._delete_symbol:
                self._delete()
            else:
                self._input += symbol
            self._set_eeg_input(symbol)
            return True

    def _set_eeg_input(self, symbol):
        self._symbol = symbol
        self._view.answered()

    def process_eeg_input(self):
        if self._triggerer:
            self._triggerer(self._symbol)
        self._view.eeg_letter(self._input, self._symbol,
                              update_word=self._update_word)

    def _delete(self):
        self._input += self._delete_symbol

class FreeSpellingInputHandler(SpellingInputHandler):
    def __init__(self, *a, **kw):
        SpellingInputHandler.__init__(self, update_word=True, *a, **kw)

    def _delete(self):
        self._input = self._input[:-1]

CopySpellingInputHandler = SpellingInputHandler
