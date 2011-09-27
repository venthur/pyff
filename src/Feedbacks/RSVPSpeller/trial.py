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
from time import sleep

from lib import marker

from RSVPSpeller.burst import BurstConstraints
from RSVPSpeller.util.trigger import BurstTriggerer, TRIG_COUNTED_OFFSET

__all__ = ['YesNoTrial', 'CountTrial', 'CalibrationTrial', 'FreeSpellingTrial',
          'CopySpellingTrial']

class Trial(object):
    def __init__(self, view, trigger, iter, seq_fac, config,
                 trial_fix_cross=False, burst_fix_cross=False,
                 trial_input=False, burst_input=False, sequence_input=False):
        self._view = view
        self._trigger = trigger
        self._iter = iter
        self._stimulus_sequence = seq_fac
        self._trial_input = trial_input
        self._burst_input = burst_input
        self._sequence_input = sequence_input
        self._triggerer = BurstTriggerer(config.nonalpha_trigger, self._trigger)
        self.__init_parameters(config)
        self.__init_attributes()

    def __init_parameters(self, config):
        self._inter_burst = config.inter_burst
        self._inter_sequence = config.inter_sequence
        self._symbol_duration = config.symbol_duration
        self._max_diff = config.max_diff
        self._trial_countdown = config.show_trial_countdown
        self._trial_fix_cross = config.show_trial_fix_cross
        self._burst_fix_cross = config.show_burst_fix_cross

    def __init_attributes(self):
        self._logger = logging.getLogger('Trial')
        self.asking = False
        self._current_target = ''

    def _burst(self, symbols):
        for symbol, color in self._iter(symbols):
            self._view.symbol(symbol, color)
            self._triggerer.symbol(symbol)
            self._triggerer()
            self._view.present(self._symbol_duration)
        self._view.clear_center_word()

    def _ask(self):
        self.asking = True
        self._view.ask()
        self.asking = False

    def _sequence(self, sequence):
        pass

    def run(self, sequences):
        self._trigger(marker.TRIAL_START, wait=True)
        self._run(sequences)
        self._trigger(marker.TRIAL_END, wait=True)

    def _run(self, sequences):
        if self._trial_countdown:
            self._view.countdown()
        if self._trial_fix_cross:
            self._view.show_fixation_cross()
        for seq in self._iter(sequences):     
            self._sequence(seq)
            if self._sequence_input:
                self._ask()
            sleep(self._inter_sequence)
        if self._trial_input:
            self._ask()

    def target(self, target):
        self._current_target = target
        self._triggerer.target(target)

    def evaluate(self, input_handler):
        pass

class OfflineTrial(Trial):
    def _sequence(self, sequence):
        """ Iterate over the sequence of symbol bursts and present them.
        The BurstConstraints object controls the display of the fixation
        cross, user input query and trigger transmission.
        """
        burst_constraints = BurstConstraints(self._burst_fix_cross,
                                             self._burst_input, self._view,
                                             self._ask, self._inter_burst,
                                             self._trigger)
        self.sequence = sequence.sequence
        for burst in self._iter(sequence.bursts):
            symbols = [b[0] for b in burst]
            with burst_constraints:
                self._target_present = self._current_target in symbols
                self._burst(burst)

class CountTrial(OfflineTrial):
    def __init__(self, *a, **kw):
        OfflineTrial.__init__(self, trial_fix_cross=True, trial_input=True,
                                  *a, **kw)

    def _run(self, sequences):
        self._count = sequences.occurences(self._current_target)
        OfflineTrial._run(self, sequences)

    def evaluate(self, input):
        diff = input.count - self._count
        constrained_diff = max(min(diff, self._max_diff), -self._max_diff)
        if diff != constrained_diff:
            self._logger.error('Too high count discrepancy: %d' % diff)
        self._trigger(TRIG_COUNTED_OFFSET + diff)

class YesNoTrial(OfflineTrial):
    def __init__(self, *a, **kw):
        OfflineTrial.__init__(self, burst_fix_cross=True, burst_input=True,
                                 *a, **kw)

class OnlineTrial(Trial):
    def _sequence(self, sequence):
        self._burst(sequence)

class SpellingTrial(OnlineTrial):
    def __init__(self, *a, **kw):
        OnlineTrial.__init__(self, trial_input=True, *a, **kw)

    def evaluate(self, input_handler):
        input_handler.process_eeg_input()

CalibrationTrial = OnlineTrial
FreeSpellingTrial = SpellingTrial
CopySpellingTrial = SpellingTrial
