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

import logging, os

import VisionEgg
from VisionEgg.Core import Screen, Viewport
from VisionEgg.FlowControl import Presentation

from pygame import Color

from lib import marker

from model.color_word import ColorWord
from model.color_word import TextList
from model.stimulus import TextureStimulus
from util.switcherator import Switcherator

class VisionEggView(object):
    """ This class handles VisionEgg internals and the creation of
    common/standard stimuli like centered words, a fixation cross or
    a countdown. Inherit this and pass the type to VisionEggFeedback
    for customization.
    """
    def __init__(self):
        self.__init_attributes()

    def __init_attributes(self):
        """ Setup internal attributes. """
        self._logger = logging.getLogger('VisionEggView')
        self._logger.addHandler(logging.FileHandler('log'))
        self._screen_acquired = False
        self._viewports = []

    def set_trigger_function(self, trigger):
        self._trigger = trigger

    def set_event_handlers(self, event_handlers):
        """ Set pygame/VisionEgg event handler function. """
        self._event_handlers = event_handlers

    def add_event_handlers(self, event_handlers):
        self._event_handlers.extend(event_handlers)

    def set_iterator_semaphore(self, flag):
        """ Specify the object to be used as semaphore for iterators.
        See L{Switcherator} for more.
        """
        self._iter = lambda it: Switcherator(flag, it)

    def update_parameters(self, **kwargs):
        """ Apply new parameters set from pyff. """
        for k, v in kwargs.iteritems():
            setattr(self, '_' + k, v)
        if self._screen_acquired:
            self.reinit()

    def acquire(self):
        """ Allow L{update_parameters} initialize VisionEgg. """
        self._screen_acquired = True

    def reinit(self):
        """ Initialize VisionEgg objects. """
        self.__init_screen()
        self.__init_presentation()
        self.__init_viewports()
        self.init()
        self.__init_text()

    def init(self):
        """ Overload this for additional custom VisionEgg
        initialization.
        """
        pass

    def __init_screen(self):
        """ Create the VisionEgg Screen object using the pyff
        configuration parameters 'fullscreen' and 'geometry' and the
        font and background colors according to parameters
        'font_color_name' and 'bg_color'.
        """
        params = { 'fullscreen': self._fullscreen, 'sync_swap': True }
        if self._fullscreen:
            params['size'] = self._fullscreen_resolution
        else:
            os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d' % (self._geometry[0],
                                                             self._geometry[1])
            params['size'] = self._geometry[2:]
        self.screen = Screen(**params)
        self._set_bg_color()
        self._set_font_color()

    def __init_presentation(self):
        """ Provide a standard presentation object. """
        self.presentation = Presentation(handle_event_callbacks=
                                         self._event_handlers)

    def __init_viewports(self):
        """ Provide a standard viewport. """
        self._standard_viewport = Viewport(screen=self.screen)
        self.add_viewport(self._standard_viewport)

    def __init_text(self):
        """ Provide a text in the screen center for standard stimuli and
        fixation cross etc.
        """
        sz = self.screen.size
        self._center_text = self.add_color_word(position=(sz[0] / 2.,
                                                          sz[1] / 2.),
                                                font_size=self._font_size)

    def add_viewport(self, viewport):
        """ Add an additional custom viewport object to the list of
        viewports.
        """
        self._viewports.append(viewport)
        self.presentation.set(viewports=self._viewports)

    def clear_stimuli(self):
        """ Remove all existing stimuli in the standard viewport. """
        self.set_stimuli()

    def add_stimuli(self, *stimuli):
        """ Add additional custom stimulus objects to the list of
        stimuli. TextList instances need their own Viewport, as they
        consist of multiple stimulus objects that are deleted everytime
        they change, and so the Viewport needs to have a reference to
        the containing TextList, otherwise they get lost.
        """
        text_lists = filter(lambda s: isinstance(s, TextList), stimuli)
        if text_lists:
            for text in text_lists:
                self.add_viewport(Viewport(screen=self.screen, stimuli=text))
            stimuli = filter(lambda s: not isinstance(s, TextList), stimuli)
        stimuli = self._standard_viewport.parameters.stimuli + list(stimuli)
        if stimuli:
            self.set_stimuli(*stimuli)

    def set_stimuli(self, *stimuli):
        """ Set the list of stimulus objects.  """
        self._standard_viewport.set(stimuli=list(stimuli))

    def add_text_stimulus(self, text, font_size=None, **kw):
        if not kw.has_key('anchor'):
            kw['anchor'] = 'center'
        font_size = font_size or self._font_size
        txt = VisionEgg.Text.Text(text=text, font_size=font_size, **kw)
        self.add_stimuli(txt)
        return txt

    def add_color_word(self, text='', font_size=None, **kw):
        font_size = font_size or self._font_size
        txt = ColorWord(text=text, symbol_size=font_size, **kw)
        self.add_stimuli(txt)
        return txt

    def add_image_stimulus(self, **kw):
        if not kw.has_key('anchor'):
            kw['anchor'] = 'center'
        img = TextureStimulus(**kw)
        self.add_stimuli(img)
        return img

    def _create_color(self, name):
        try:
            if isinstance(name, tuple):
                return Color(*name).normalize()
            else:
                return Color(str(name)).normalize()
        except ValueError:
            self._logger.warn('No such pygame.Color: %s' % str(name))

    def _set_font_color(self):
        """ Set the standard font color by pygame name. """
        self._font_color = (self._create_color(self._font_color_name) or
                            Color(1, 1, 1, 255).normalize())

    def _set_bg_color(self):
        """ Set the standard background color by pygame name. """
        c = (self._create_color(self._bg_color) or
             Color(0, 0, 0, 255).normalize())
        self.screen.set(bgcolor=c)

    def present_frames(self, num_frames):
        """ Launch the presentation main loop for a given number of
        frames.
        """
        self.presentation.set(go_duration=(num_frames, 'frames'))
        self.presentation.go()

    def present(self, sec):
        self.presentation.set(go_duration=(sec, 'seconds'))
        self.presentation.go()

    def update(self):
        """ Repaint the canvas for one frame to update changed stimuli.
        """
        self.present_frames(1)

    def center_word(self, text, color=None):
        """ Set the standard word in the screen center. """
        self._center_text.set(text=text)
        self._center_text.set(colors=color or (self._font_color for l in
                                           self._center_text))

    def word(self, word):
        pass

    def eeg_letter(self, *a, **kw):
        pass

    def next_target(self):
        pass

    def previous_target(self):
        pass

    def clear_center_word(self):
        """ Remove the center word from the screen. """
        self.center_word('')
        self.update()

    def present_center_word(self, text, seconds, color=None):
        self.center_word(text, color)
        self.present(seconds)
        self.clear_center_word()

    def ask(self, question=True):
        """ Loop indefinitely until answered() is called. If question is
        True, a question mark is shown in the center.
        """
        if question:
            self.center_word('?')
        self.presentation.run_forever()
        self.presentation.set(quit=False)
        self.clear_center_word()

    def answered(self):
        """ Abort the current presentation (usually the question mark)
        after subject input. For thread safety, the screen shouldn't be
        changed here.
        """
        self.presentation.set(quit=True)

    def show_fixation_cross(self):
        """ Display the pyff parameter 'fixation_cross_symbol' for the
        period of time given by pyff parameter 'fixation_cross_time'.
        """
        self.center_word(self._fixation_cross_symbol)
        self._trigger(marker.FIXATION_START, wait=True)
        self.present(self._fixation_cross_time)
        self._trigger(marker.FIXATION_END, wait=True)

    def countdown(self):
        """ Display a countdown according to pyff parameters
        'countdown_start' and 'countdown_symbol_duration'.
        """
        self._trigger(marker.COUNTDOWN_START, wait=True)
        for i in self._iter(reversed(xrange(self._countdown_start + 1))):
            self.center_word(str(i))
            self.present(self._countdown_symbol_duration)
        self._trigger(marker.COUNTDOWN_END, wait=True)
        self.clear_center_word()

    def close(self):
        """ Shut down the screen. """
        self._screen_acquired = False
        self.screen.close()

    def quit(self):
        """ Stop the presentation. """
        self.presentation.set(quit=True)
        self.presentation.set(go_duration=(1, 'frames'))
