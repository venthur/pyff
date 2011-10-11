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

from RSVPSpeller.util.trigger import (EEGTriggerer, TRIG_TARGET_PRESENT_OFFSET,
                                     TRIG_TARGET_ABSENT_OFFSET)

__all__ = ['CountInputHandler', 'YesNoInputHandler', 'CalibrationInputHandler',
           'CopySpellingInputHandler', 'FreeSpellingInputHandler']

class InputHandler(object):
    def __init__(self, control):
        self._view = control._view
        self._trigger = control._trigger
        self._triggerer = EEGTriggerer(control.nonalpha_trigger, self._trigger)

    def start_experiment(self, experiment):
        self._experiment = experiment

    def start_trial(self, trial):
        self._trial = trial

class CountInputHandler(InputHandler):
    def __init__(self, control):
        self._digits = ''
        InputHandler.__init__(self, control)

    def start_trial(self, trial):
        InputHandler.start_trial(self, trial)
        self._digits = ''

    def keyboard(self, event):
        s = event.unicode
        if self._digits:
            if event.key == pygame.K_RETURN:
                self._process_keyboard_input()
                self._digits = ''
            elif event.key == pygame.K_BACKSPACE:
                self._digits = self._digits[:-1]
        elif s.isdigit():
            self._digits += s
        else:
            return False
        return True

    def _process_keyboard_input(self):
        self.count = int(self._digits)
        self._view.answered()

class YesNoInputHandler(InputHandler):
    def __init__(self, control):
        self._key_yes = control.key_yes
        self._key_no = control.key_no
        InputHandler.__init__(self, control)

    def start_trial(self, trial):
        InputHandler.start_trial(self, trial)
        self.detections = []

    def keyboard(self, event):
        """ Yes/No mode. Save the answer in the detections list, send
        a trigger. The trigger value is determined by the presence of
        the target and the subject's detection: 11 for no target, no
        detection; 22 for present target and detection; and the false
        variants with 12/21 in the same order. """
        s = event.unicode
        if s in [self._key_yes, self._key_no]:
            yes = s == self._key_yes
            self.detections.append(yes)
            trig = TRIG_TARGET_PRESENT_OFFSET if self._trial._target_present \
                   else TRIG_TARGET_ABSENT_OFFSET
            self._trigger(trig + yes)
            self._view.answered()

CalibrationInputHandler = InputHandler

class SpellingInputHandler(CountInputHandler):
    def __init__(self, control, update_word=False, *a, **kw):
        self._update_word = update_word
        self._delete_symbol = control.delete_symbol
        self._alphabet = list(control.eeg_alphabet)
        self._allow_keyboard = control.allow_keyboard_input
        self._input = ''
        self._symbol = ''
        self._eeg_input_processed = True
        CountInputHandler.__init__(self, control, *a, **kw)

    def keyboard(self, event):
        s = event.unicode
        if (self._allow_keyboard and not CountInputHandler.keyboard(self, event)
            and s in self._alphabet):
            self.eeg_select(self._alphabet.index(s))

    def _process_keyboard_input(self):
        self.eeg_select(int(self._digits) - 1)

    def eeg_select(self, cls):
        if 0 <= cls < len(self._alphabet):
            symbol = self._alphabet[cls]
            print "Received control signal: %s -> %s" % (str(cls), symbol)
            if symbol == self._delete_symbol:
                self._delete()
            else:
                self._input += symbol
            self._set_eeg_input(symbol)
            return True

    def _set_eeg_input(self, symbol):
        self._symbol = symbol
        self._eeg_input_processed = False
        self._view.answered()

    def process_eeg_input(self):
        if not self._eeg_input_processed:
            self._triggerer.symbol(self._symbol)
            self._triggerer()
            self._view.eeg_letter(self._input, self._symbol,
                                  update_word=self._update_word)
            self._eeg_input_processed = True

    def _delete(self):
        self._input += self._delete_symbol

class FreeSpellingInputHandler(SpellingInputHandler):
    def __init__(self, *a, **kw):
        SpellingInputHandler.__init__(self, update_word=True, *a, **kw)

    def _delete(self):
        self._input = self._input[:-1]

CopySpellingInputHandler = SpellingInputHandler
