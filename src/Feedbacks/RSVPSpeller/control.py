from __future__ import with_statement

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

from os import path

import pygame

from FeedbackBase.VisionEggFeedback import VisionEggFeedback

from RSVPSpeller.config import Config
from RSVPSpeller.view import View
from RSVPSpeller.model.palette import Palette
from RSVPSpeller.util.metadata import datadir
from RSVPSpeller.trial import *
from RSVPSpeller.input import *
from RSVPSpeller.experiment import *
from RSVPSpeller.util.error import RSVPSpellerException

class Control(VisionEggFeedback, Config):
    def __init__(self, *args, **kwargs):
        pygame.mixer.init()
        self.__init_attributes()
        VisionEggFeedback.__init__(self, *args, **kwargs)

    def init(self):
        Config.init(self)
        self.update_parameters()

    def __init_attributes(self):
        self._sound = pygame.mixer.Sound(path.join(datadir, 'sound.ogg'))
        self._palette = Palette()
        self._trial_types = ['Count', 'YesNo', 'Calibration', 'FreeSpelling',
                             'CopySpelling']

    def _create_view(self):
        return View(self._palette)

    def update_parameters(self):
        VisionEggFeedback.update_parameters(self)
        self._palette.set(self.symbol_colors, self.color_groups)
        self.alphabet = ''.join(self.color_groups)
        self._sorted_alphabet = sorted(self.alphabet, key=lambda s: s.lower())
        self.eeg_alphabet = ''.join(filter(lambda c: c.isalpha(),
                                           self._sorted_alphabet)
                                    + [e[0] for e in self.nonalpha_trigger])
        self._trial_name = self._trial_types[self.trial_type - 1]
        self._setup_input_handler()
        self._setup_trial()
        self._setup_experiment()

    def _setup_input_handler(self):
        input_handler_type = self._trial_name + 'InputHandler'
        self._input_handler = eval(input_handler_type)(self)

    def _setup_trial(self):
        trial_type = self._trial_name + 'Trial'
        self._trial = eval(trial_type)(self._view, self._trigger, self._iter,
                                       self.stimulus_sequence, self)

    def _setup_experiment(self):
        experiment_type = self._trial_name + 'Experiment'
        self._experiment = eval(experiment_type)(self._view, self._trial,
                                                 self._input_handler,
                                                 self._flag, self._iter,
                                                 self._palette, self)

    def run(self):
        try:
            self._view.alphabet(self.eeg_alphabet)
            self._experiment.run()
        except RSVPSpellerException as e:
            self.logger.error(e)
        self.quit()

    def keyboard_input(self, event):
        if self._trial.asking:
            self._input_handler.keyboard(event)
        VisionEggFeedback.keyboard_input(self, event)

    def quit(self):
        self._view.answered()
        VisionEggFeedback.quit(self)

    def on_control_event(self, data):
        cls = data.get('cl_output', None)
        if cls is not None:
            self._input_handler.eeg_select(cls)

class RSVPSpeller(Control):
    pass
