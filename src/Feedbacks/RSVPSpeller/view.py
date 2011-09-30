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

import logging

from VisionEgg.Core import *

from lib import marker
from lib.vision_egg import VisionEggView

from RSVPSpeller.model.target_word import TargetWord

class View(VisionEggView):
    def __init__(self, palette):
        self._palette = palette
        self.__init_attributes()
        VisionEggView.__init__(self)

    def __init_attributes(self):
        self._logger = logging.getLogger('View')
        self._symbol_duration = 0.05
        self._font_size = 150

    def reinit(self):
        VisionEggView.reinit(self)
        sz = self.screen.size
        self._center_text.set_position((sz[0] / 2., sz[1] - self._symbol_vpos))

    def init(self):
        self.__init_text()

    def __init_text(self):
        """ Initialize the target word and alphabet texts and adjust
        the symbol position.
        """
        sz = self.screen.size
        self._word = TargetWord(position=(sz[0] / 2., sz[1] -
                                              self._word_vpos),
                                    symbol_size=self._word_font_size,
                                    target_size=self._word_target_font_size,
                                    target_frame=self._show_target_frame,
                                    target_frame_width=self._target_frame_width,
                                    center_at_target=True)
        self.add_stimuli(self._word)
        if self._show_alphabet:
            self._alphabet = self.add_color_word(position=(sz[0] / 2., sz[1] -
                                                           self._alphabet_vpos),
                                                 font_size=
                                                 self._alphabet_font_size)

    def _symbol_color(self, symbol):
        return self._palette(symbol) if self._alternating_colors else \
               self._font_color

    def alphabet(self, alphabet):
        if self._show_alphabet:
            colors = map(self._symbol_color, alphabet)
            self._alphabet.set(text=alphabet, colors=colors)

    def word(self, word):
        """ Introduce a new word, optionally with colored symbols. """
        self._word.set_all(on=False)
        colors = map(self._symbol_color, word)
        self.center_word(word, colors)
        self.present(self._present_word_time)
        self._word.set(text=word, colors=colors)

    def target(self, index):
        """ Introduce a new target symbol by increasing its size and
        presenting the word in the headline.
        """
        self._word.set(target=index)
        self._word.set_all(on=True)
        self._center_text.set_all(on=False)
        self.present(self._present_target_time)
        self._center_text.set_all(on=True)

    def eeg_letter(self, text, symbol, update_word=True):
        self._trigger(marker.FEEDBACK_START, wait=True)
        colors = map(self._symbol_color, text)
        self.symbol(symbol, self._symbol_color(symbol))
        self.present(self._present_eeg_input_time)
        self._center_text.set_all(on=False)
        self._trigger(marker.FEEDBACK_END, wait=True)
        if update_word:
            self._word.set(text=text, target=len(text)-1, colors=colors)

    def symbol(self, symbol, color=None):
        """ Display a single symbol, either in the standard font color
        or using the function parameter.
        """
        if color is None:
            color = self._font_color
        self.center_word(symbol, (color,))
