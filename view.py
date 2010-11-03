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

import logging

from VisionEgg.Core import *

from pygame import Color

from lib.vision_egg import VisionEggView
from lib.vision_egg.model.color_word import ColorWord

from AlphaBurst.util.switcherator import Switcherator

class View(VisionEggView):
    def __init__(self, palette):
        self._palette = palette
        self.__init_attributes()
        VisionEggView.__init__(self)

    def __init_attributes(self):
        self._logger = logging.getLogger('View')
        self._symbol_duration = 0.05
        self._font_size = 150

    def acquire(self):
        self._screen_acquired = True

    def init(self):
        self.__init_text()
        self.__init_viewports()

    def __init_text(self):
        """ Calculate the height of the headline from the font size and
        set positions accordingly.
        """
        sz = self.screen.size
        self._headline = ColorWord((sz[0] / 2., sz[1] - self._headline_vpos),
                                   symbol_size=self._headline_font_size,
                                   target_size=self._headline_target_font_size)
        self._center_text = ColorWord((sz[0] / 2., sz[1] - self._symbol_vpos),
                                      symbol_size=self._font_size)

    def __init_viewports(self):
        self._headline_viewport = Viewport(screen=self.screen,
                                           stimuli=self._headline)
        self._viewport = Viewport(screen=self.screen,
                                  stimuli=self._center_text)
        self.add_viewport(self._headline_viewport)
        self.add_viewport(self._viewport)

    def _symbol_color(self, symbol):
        return self._palette(symbol) if self._alternating_colors else \
               self._font_color

    def word(self, word):
        """ Introduce a new word, optionally with colored symbols.
        """
        self._headline.set_all(on=False)
        colors = map(self._symbol_color, word)
        self._center_word(word, colors)
        self._present(self._present_word_time)
        self._headline.set(text=word, colors=colors)

    def target(self, symbol):
        """ Introduce a new target symbol by increasing its size and
        presenting the word in the headline.
        """
        self._headline.set(target=symbol)
        self._headline.set_all(on=True)
        self._center_text.set_all(on=False)
        self._present(self._present_target_time)
        self._center_text.set_all(on=True)

    def _present(self, sec):
        self.presentation.set(go_duration=(sec, 'seconds'))
        self.presentation.go()

    def _center_word(self, text, color=None):
        self._center_text.set(text=text)
        self._center_text.set(colors=color or (self._font_color for l in
                                           self._center_text))

    def ask(self):
        self._center_word('?')
        self._asking = True
        self.presentation.run_forever()
        self.presentation.set(quit=False)

    def answered(self):
        """ Abort the current presentation (normally the question mark)
        after subject input.
        """
        self.presentation.set(quit=True)

    def show_fixation_cross(self):
        self._center_word('+')
        self._present(self._fixation_cross_time)

    def symbol(self, symbol, color=None):
        """ Display a single symbol, either in the standard font color
        or using the function parameter.
        """
        if color is None:
            color = self._font_color
        self._center_word(symbol, (color,))

    def clear_symbol(self):
        """ Remove the stimulus from the screen. Alternatives welcome.
        """
        self._center_text.set_all(on=False)
        self._present(0.0000000001)
        self._center_text.set_all(on=True)

    def count_down(self):
        for i in self._iter(reversed(xrange(self._count_down_start + 1))):
            self._center_word(str(i))
            self._present(self._count_down_symbol_duration)
        self.clear_symbol()
