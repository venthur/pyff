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

import logging

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation
from VisionEgg.Text import Text

from pygame import Color

from AlphaBurst.model.color_word import ColorWord

class View(object):
    def __init__(self, width, height, fullscreen):
        self._screen = Screen(size=(width, height), fullscreen=fullscreen)
        self.__init_attributes()
        self.__init_text()
        self.__init_viewports()
        self.__init_presentation()

    def __init_attributes(self):
        self._logger = logging.getLogger('View')
        self._symbol_duration = 0.05
        self.update_parameters()

    def __init_text(self):
        sz = self._screen.size
        self._headline = ColorWord((sz[0] / 2., -100 + sz[1]))
        self._center_text = Text(font_size=150, anchor='center',
                              position=(sz[0] / 2., -50 + sz[1] / 2.))

    def __init_viewports(self):
        self._headline_viewport = Viewport(screen=self._screen,
                                           stimuli=self._headline)
        self._viewport = Viewport(screen=self._screen,
                                  stimuli=[self._center_text])

    def __init_presentation(self):
        self.presentation = Presentation(viewports=[self._headline_viewport,
                                                    self._viewport])

    def update_parameters(self, font_color='white', bg_color='grey', **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, '_' + k, v)
        self.set_bg_color(bg_color)
        self.set_font_color(font_color)

    def set_font_color(self, color):
        try:
            self._font_color = Color(color).normalize()
        except ValueError:
            self._logger.warn('No such pygame.Color: %s' % str(color))

    def set_bg_color(self, color):
        try:
            self._screen.set(bgcolor=Color(color).normalize())
        except ValueError:
            self._logger.warn('No such pygame.Color: %s' % str(color))

    def present_word(self, word, target_index):
        self._center_word(word)
        self._present(2)
        self._headline.set(word, word[target_index])

    def _present(self, sec):
        self.presentation.set(go_duration=(sec, 'seconds'))
        self.presentation.go()

    def _center_word(self, text, color=None):
        self._center_text.set(text=text, color=color or self._font_color)

    def ask(self):
        self._center_word('?')
        self._asking = True
        self.presentation.run_forever()
        self.presentation.set(quit=False)

    def answered(self):
        self.presentation.set(quit=True)

    def set_duration(self, secs):
        self.presentation.set(go_duration=(secs, 'seconds'))

    def show_fixation_cross(self):
        self._center_word('+')
        self._present(1)

    def adjust_symbol_colors(self, sequence):
        colors = [sequence.get_color(t) or self._font_color for t in
                  self._headline.text]
        self._headline.set_colors(colors)

    def burst(self, symbols):
        for symbol in symbols:
            self.symbol(*symbol)
        #TODO less ugly
        self._center_text.set(on=False)
        self._present(0.0000000001)
        self._center_text.set(on=True)

    def symbol(self, symbol, color=None):
        self._center_word(symbol, color)
        self._present(self._symbol_duration)
