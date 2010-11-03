from __future__ import with_statement

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

from time import sleep
from os import path

import pygame

from FeedbackBase.VisionEggFeedback import VisionEggFeedback

from AlphaBurst.config import Config
from AlphaBurst.view import View
from AlphaBurst.burst import BurstConstraints
from AlphaBurst.model.character_sequence import CharacterSequenceFactory
from AlphaBurst.model.palette import Palette
from AlphaBurst.util.metadata import datadir
from AlphaBurst.util.trigger import *
from AlphaBurst.util.switcherator import *
from AlphaBurst.trial import CountTrial, YesNoTrial
from AlphaBurst.input import CountInputHandler, YesNoInputHandler

class Control(VisionEggFeedback, Config):
    def __init__(self, *args, **kwargs):
        pygame.mixer.init()
        self.__init_attributes()
        VisionEggFeedback.__init__(self, *args, **kwargs)

    def init(self):
        Config.init(self)
        self.update_parameters()

    def __init_attributes(self):
        self._asking = False
        self._digits = ''
        self._sound = pygame.mixer.Sound(path.join(datadir, 'sound.ogg'))
        self._trigger = self.send_parallel
        self.count = 0
        self._palette = Palette()

    def _create_view(self):
        return View(self._palette)

    def update_parameters(self):
        VisionEggFeedback.update_parameters(self)
        self._trials = [CountTrial, YesNoTrial]
        trial_type = self._trials[self.trial_type - 1]
        self._trial = trial_type(self._view, self._trigger, self._iter,
                                   self.stimulus_sequence, self)
        input_handlers = [CountInputHandler, YesNoInputHandler]
        input_handler_type = input_handlers[self.trial_type - 1]
        self._input_handler = input_handler_type(self)
        self._palette.set(self.symbol_colors, self.color_groups)
        self._alphabet = ''.join(self.color_groups)

    def play_tick(self):
        try:
            if self.sound:
                self._sound.play()
            self.block()
        except pygame.error, e:
            self.logger.error(e)
        self.quit()

    def block(self):
        for word in self._iter(self.words):
            self._view.count_down()
            self._view.word(word)
            gen = self._iter(enumerate(word))
            for self.target_index, self._current_target in gen:
                self.trial()

    def trial(self):
        sleep(self.inter_trial)
        factory = CharacterSequenceFactory(self.meaningless,
                                           self.alternating_colors,
                                           self._current_target,
                                           self._palette)
        self._sequences = factory.sequences(self.sequences_per_trial,
                                            self.custom_pre_sequences,
                                            self.custom_post_sequences)
        self.detections = []
        self._view.target(self._current_target)
        self._input_handler.start_trial(self._trial)
        self._trial.run(self._sequences, self._current_target)
        if self._flag:
            self._input_handler.set_result(self)
            self._trial.evaluate(self._input_handler)

    def keyboard_input(self, event):
        if self._trial.asking:
            self._input_handler.keyboard(event)
        VisionEggFeedback.keyboard_input(self, event)

    def quit(self):
        self._view.answered()
        VisionEggFeedback.quit(self)

class AlphaBurst(Control):
    pass
