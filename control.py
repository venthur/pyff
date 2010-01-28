""" {{{ Copyright (c) 2009 Torsten Schmits

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
import string

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import Text

from FeedbackBase.MainloopFeedback import MainloopFeedback
from AlphaBurst.model.letter_sequence import LetterSequence

class Control(MainloopFeedback):
    def init(self):
        self.__init_config()
        self._screen = get_default_screen()
        self.__init_text()
        self.__init_viewports()
        self.__init_presentation()

    def __init_config(self):
        self.alphabet = string.ascii_uppercase + ',.;:!?'
        self.burst_duration = 
        self.update_parameters()

    def __init_text(self):
        sz = self._screen.size
        self._headline = Text(font_size=72, text='Do something!',
                              anchor='center', position=(sz[0] / 2., -50 +
                                                         sz[1]))
        self._stimulus = Text(font_size=150, anchor='center',
                              position=(sz[0] / 2., -50 + sz[1] / 2.))

    def __init_viewports(self):
        self._headline_viewport = Viewport(screen=self._screen,
                                           stimuli=[self._headline])
        self._viewport = Viewport(screen=self._screen, stimuli=[self._stimulus])

    def __init_presentation(self):
        self._presentation = Presentation(viewports=[self._headline_viewport,
                                                     self._viewport])

    def update_parameters(self):
        self._letter_sequence = LetterSequence(self.alphabet)

    def play_tick(self):
        if self._letter_sequence.done:
            self.on_stop()
        else:
            self._burst()
            self._ask()

    def on_interaction_event(self, data):
        self.update_parameters()

    def _burst(self):
        for letter in self._letter_sequence.next_burst:
            self._stimulus.set(text=letter)
            self._presentation.set(go_duration=(0.05, 'seconds'))
            self._presentation.go()

    def _ask(self):
        self._stimulus.set(text='?')
        self._presentation.set(go_duration=(5, 'seconds'))
        self._presentation.go()
