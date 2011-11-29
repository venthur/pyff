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
from itertools import count
import logging

__all__ = ['CopySpellingExperiment', 'CalibrationExperiment',
           'FreeSpellingExperiment']

class Experiment(object):
    def __init__(self, view, trial, phrases, input_handler, flag, iter, config):
        self._view = view
        self._trial = trial
        self._phrases = phrases
        self._input_handler = input_handler
        self._flag = flag
        self._iter = iter
        self._current_target = ''
        self._inter_trial = config.inter_trial
        self._inter_phrase = config.inter_phrase
        self._countdown = config.phrase_countdown
        self._target_present_time = config.target_present_time
        self._sequences = lambda: []

    def run(self):
        self._input_handler.start_experiment(self)

    def trial(self):
        self._input_handler.start_trial(self._trial)
        self._trial.run(self._sequences())
        if self._flag:
            self._trial.evaluate(self._input_handler)

    def delete(self):
        pass

    def sequences(self):
        pass

class GuidedExperiment(Experiment):
    def run(self):
        super(GuidedExperiment, self).run()
        for word in self._iter(self._phrases):
            self._view.word(word)
            if self._countdown:
                self._view.countdown()
            for target in self._iter(enumerate(word)):
                self.trial(*target)
                sleep(self._inter_trial)
            sleep(self._inter_phrase)

    def trial(self, index, target):
        self._trial.target(target)
        self._view.present(self._target_present_time)
        Experiment.trial(self)
        if self._flag:
            self._view.next_target()

CopySpellingExperiment = GuidedExperiment
CalibrationExperiment = GuidedExperiment

class FreeSpellingExperiment(Experiment):
    def run(self):
        super(FreeSpellingExperiment, self).run()
        for i in self._iter(count()):
            self.trial()
