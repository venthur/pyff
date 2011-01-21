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

from lib import marker

__all__ = ['CalibrationTrial', 'FreeSpellingTrial', 'CopySpellingTrial']

class Trial(object):
    def __init__(self, view, trigger, iter, config, trial_input=False):
        self._view = view
        self._trigger = trigger
        self._iter = iter
        self._countdown = config.trial_countdown
        self._trial_input = trial_input
        self.__init_attributes()

    def __init_attributes(self):
        self.asking = False
        self.current_target = ''

    def _ask(self):
        self.asking = True
        self._view.ask()
        self.asking = False

    def _sequence(self):
        pass

    def run(self, sequences):
        self._trigger(marker.TRIAL_START, wait=True)
        self._run(sequences)
        self._trigger(marker.TRIAL_END, wait=True)

    def _run(self, sequences):
        if self._countdown:
            self._view.countdown()
        for seq in self._iter(sequences):     
            self._sequence(seq)
        if self._trial_input:
            self._ask()

    def target(self, target):
        self.current_target = target

    def evaluate(self, input_handler):
        pass

class SpellingTrial(Trial):
    def __init__(self, *a, **kw):
        Trial.__init__(self, trial_input=True, *a, **kw)

    def evaluate(self, input_handler):
        input_handler.process_eeg_input()

CalibrationTrial = Trial
FreeSpellingTrial = SpellingTrial
CopySpellingTrial = SpellingTrial
