""" {{{ Copyright (c) 2010 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

}}} """

from __future__ import with_statement

from time import sleep
from os import path
import logging

import pygame

import VisionEgg

from FeedbackBase.Feedback import Feedback

from AlphaBurst.config import Config
from AlphaBurst.view import View
from AlphaBurst.burst import BurstConstraints
from AlphaBurst.model.character_sequence import CharacterSequenceFactory
from AlphaBurst.util.metadata import datadir
from AlphaBurst.util.trigger import *
from AlphaBurst.util.switcherator import *

VisionEgg.config.VISIONEGG_GUI_INIT = 0
VisionEgg.config.VISIONEGG_LOG_TO_STDERR = 0
VisionEgg.logger.setLevel(logging.ERROR)

class Control(Feedback, Config):
    def __init__(self, *args, **kwargs):
        Feedback.__init__(self, *args, **kwargs)
        pygame.mixer.init()
        self.__init_attributes()

    def on_init(self):
        Config.init(self)
        self.update_parameters()

    def __init_attributes(self):
        self._view_started = False
        self._asking = False
        self._digits = ''
        self._sound = pygame.mixer.Sound(path.join(datadir, 'sound.ogg'))
        self._logger = logging.getLogger('Control')
        self._logger.setLevel(logging.DEBUG)
        self._trigger = self.send_parallel
        self.count = 0

    def _start_view(self):
        self._view = View(self.screen_width, self.screen_height,
                          self.fullscreen)
        self._view_started = True
        handlers = [(pygame.KEYDOWN, self.keyboard_input)]
        self._view.presentation.set(handle_event_callbacks=handlers)

    def update_parameters(self):
        self._trial_type = getattr(self, '_trial_' + str(self.trial_type))
        self._process_input = getattr(self, '_process_input_' +
                                      str(self.trial_type))
        if self._view_started:
            params = dict([[p, getattr(self, p, None)] for p in
                           self._view_parameters])
            self._view.update_parameters(**params)

    def on_interaction_event(self, data):
        self.update_parameters()

    def on_play(self):
        self._flag = Flag()
        self._iter = lambda it: Switcherator(self._flag, it)
        self._start_view()
        self.update_parameters()
        if self.sound:
            self._sound.play()
        self._block()
        self.on_stop()

    def _block(self):
        for word in self._iter(self.words):
            self._view.present_word(word)
            gen = self._iter(enumerate(word))
            for self.target_index, self._current_target in gen:
                self._trial()

    def _trial(self):
        factory = CharacterSequenceFactory(self.meaningless,
                                           self.alternating_colors)
        self._sequences = factory.sequences(self.sequences_per_trial,
                                            self.custom_pre_sequences,
                                            self.custom_post_sequences)
        self.detections = []
        self._trial_type()

    def _trial_1(self):
        """ Count mode. """
        self._view.show_fixation_cross()
        for seq in self._iter(self._sequences):     
            self._sequence(seq)
        self._ask()
        diff = self.count - self._sequences.occurences(self._current_target) 
        self._trigger(TRIG_COUNTED_OFFSET + diff)

    def _trial_2(self):
        """ Yes/No mode. """
        for seq in self._iter(self._sequences):     
            self.detections.append([])
            self._sequence(seq, True, True)

    def _sequence(self, sequence, fix=False, ask=False):
        self._view.adjust_symbol_colors(sequence,
                                        self._current_target)
        self._burst_constraints = BurstConstraints(fix, ask,
                                                   self._view,
                                                   self._ask, self.inter_burst,
                                                   self._trigger)
        for burst in self._iter(sequence):
            with self._burst_constraints:
                self._burst(burst)
        sleep(self.inter_sequence)

    def _burst(self, symbols):
        for symbol in self._iter(symbols):
            try:
                self._trigger(symbol_trigger(symbol[0], self._current_target,
                                             self.alphabet))
            except ValueError:
                # redundant symbol
                pass
            self._view.symbol(*symbol)

    def _ask(self):
        self._asking = True
        self._view.ask()
        self._asking = False

    def keyboard_input(self, event):
        if event.key == pygame.K_q or event.type == pygame.QUIT:
            self.on_stop()
            self._view.answered()
        elif self._asking:
            self._process_input(event)

    def _process_input_1(self, event):
        """ Count mode. """
        s = event.unicode
        if event.key == pygame.K_RETURN:
            self.count = int(self._digits)
            self._digits = ''
            self._view.answered()
        elif self._digits and event.key == pygame.K_BACKSPACE:
            del self._digits[-1]
        elif s.isdigit():
            self._digits += s

    def _process_input_2(self, event):
        """ Yes/No mode. """
        s = event.unicode
        if s in [self.key_yes, self.key_no]:
            self.detections[-1].append(s == self.key_yes)
            self._view.answered()

    def on_stop(self):
        self._flag.off()

class AlphaBurst(Control):
    pass
