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

from time import sleep
from os import path
import logging

import pygame

import VisionEgg

from FeedbackBase.MainloopFeedback import MainloopFeedback

from AlphaBurst.config import Config
from AlphaBurst.view import View
from AlphaBurst.model.character_sequence import CharacterSequenceFactory
from AlphaBurst.util.metadata import datadir

VisionEgg.config.VISIONEGG_GUI_INIT = 0
VisionEgg.config.VISIONEGG_LOG_TO_STDERR = 0
VisionEgg.logger.setLevel(logging.ERROR)

class Control(MainloopFeedback, Config):
    def __init__(self, *args, **kwargs):
        MainloopFeedback.__init__(self, *args, **kwargs)
        pygame.mixer.init()
        self.__init_attributes()

    def init(self):
        Config.init(self)
        self.update_parameters()

    def __init_attributes(self):
        self._view_started = False
        self._asking = False
        self._digits = ''
        self._sound = pygame.mixer.Sound(path.join(datadir, 'sound.ogg'))
        self.logger = logging.getLogger('Control')
        self.logger.setLevel(logging.DEBUG)

    def pre_mainloop(self):
        self._start_view()
        self.update_parameters()
        if self.sound:
            self._sound.play()

    def _start_view(self):
        self._view = View(self.screen_width, self.screen_height,
                          self.fullscreen)
        self._view_started = True
        self._view.presentation.set(handle_event_callbacks=[(pygame.KEYDOWN,
                                                           self.keyboard_input)])

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

    def play_tick(self):
        self._block()
        self.on_stop()

    @property
    def _current_word(self):
        return self.words[self.current_word_index]

    def _block(self):
        self._view.present_word(self._current_word, 2)
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
        """ Count mode.

        """
        self._view.show_fixation_cross()
        while self._running and not self._sequences.done:
            self._sequence()
            self._sequences.next()
        self._ask()

    def _trial_2(self):
        """ Yes/No mode.

        """
        while self._running and not self._sequences.done:
            self.detections.append([])
            self._sequence(True, True)
            self._sequences.next()

    def _sequence(self, fix=False, ask=False):
        self._view.adjust_symbol_colors(self._sequences.current_sequence)
        while self._running and not self._sequences.sequence_done:
            if fix:
                self._view.show_fixation_cross()
            self._view.burst(self._sequences.next_burst)
            if ask:
                self._ask()
            sleep(self.inter_burst)
        sleep(self.inter_sequence)

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
        """ Count mode.

        """
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
        """ Yes/No mode.

        """
        s = event.unicode
        if s in [self.key_yes, self.key_no]:
            self.detections[-1].append(s == self.key_yes)
            self._view.answered()

class AlphaBurst(Control):
    pass
