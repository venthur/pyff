""" {{{ Copyright (c) 2010 Torsten Schmits

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

}}} """

import logging

from VisionEgg.Core import *
from VisionEgg.FlowControl import Presentation

from pygame import Color

from .model.color_word import ColorWord
from .util.switcherator import *

class VisionEggView(object):
    def __init__(self):
        self.__init_attributes()

    def __init_attributes(self):
        self._logger = logging.getLogger('VisionEggView')
        self._logger.addHandler(logging.FileHandler('log'))
        self._screen_acquired = False
        self._viewports = []

    def set_event_handlers(self, event_handlers):
        self._event_handlers = event_handlers

    def set_iterator_semaphore(self, flag):
        self._iter = lambda it: Switcherator(flag, it)

    def update_parameters(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, '_' + k, v)
        if self._screen_acquired:
            self.reinit()

    def acquire(self):
        self._screen_acquired = True

    def reinit(self):
        self._logger.error('reinit')
        self.__init_screen()
        self.__init_text()
        self.__init_presentation()
        self.__init_viewports()
        self.init()

    def init(self):
        pass

    def __init_screen(self):
        params = { 'fullscreen': self._fullscreen, 'sync_swap': True }
        if not self._fullscreen:
            os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d' % (self._geometry[0],
                                                            self._geometry[1])
            params['size'] = self._geometry[2:]
        self.screen = Screen(**params)
        self._set_bg_color()
        self._set_font_color()

    def __init_text(self):
        sz = self.screen.size
        self._center_text = ColorWord((sz[0] / 2., sz[1] / 2.),
                                      symbol_size=self._font_size)

    def __init_viewports(self):
        self._standard_viewport = Viewport(screen=self.screen,
                                         stimuli=self._center_text)
        self.add_viewport(self._standard_viewport)

    def __init_presentation(self):
        self.presentation = Presentation(handle_event_callbacks=
                                         self._event_handlers)

    def add_viewport(self, viewport):
        self._viewports.append(viewport)
        self.presentation.set(viewports=self._viewports)

    def add_stimuli(self, *stimuli):
        stimuli = self._standard_viewport.parameters.stimuli + list(stimuli)
        self.set_stimuli(*stimuli)

    def set_stimuli(self, *stimuli):
        self._standard_viewport.set(stimuli=stimuli)

    def _set_font_color(self):
        try:
            self._font_color = Color(self._font_color_name).normalize()
        except ValueError:
            self._logger.warn('No such pygame.Color: %s' %
                              str(self._font_color_name))

    def _set_bg_color(self):
        try:
            self._logger.error('bg before')
            self.screen.set(bgcolor=Color(self._bg_color).normalize())
            self._logger.error('bg after')
        except ValueError:
            self._logger.warn('No such pygame.Color: %s' % str(self._bg_color))

    def present_frames(self, num_frames):
        self.presentation.set(go_duration=(num_frames, 'frames'))
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

    def close(self):
        """ Shut down the screen. """
        self._screen_acquired = False
        self.screen.close()

    def quit(self):
        self.presentation.set(quit=True)
