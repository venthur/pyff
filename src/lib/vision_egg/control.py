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

import VisionEgg
import pygame

from FeedbackBase.MainloopFeedback import MainloopFeedback

from .view import VisionEggView
from .config import Config
from .model.stimulus import StimulusSequenceFactory
from .util.switcherator import *

VisionEgg.config.VISIONEGG_GUI_INIT = 0
VisionEgg.config.VISIONEGG_LOG_TO_STDERR = 0
VisionEgg.logger.setLevel(logging.ERROR)

class VisionEggFeedback(MainloopFeedback, Config):
    def __init__(self, view_type=VisionEggView, *args, **kwargs):
        MainloopFeedback.__init__(self, *args, **kwargs)
        Config.__init__(self)
        self._view_type = view_type
        self.__init_attributes()

    def __init_attributes(self):
        self._view = self._create_view()
        self.add_viewport = self._view.add_viewport
        self.add_stimuli = self._view.add_stimuli
        self.set_stimuli = self._view.set_stimuli
        self.set_iterator_semaphore(Flag())
        self.__setup_events()
        self.__setup_stim_factory()

    def __setup_stim_factory(self):
        refresh = VisionEgg.config.VISIONEGG_MONITOR_REFRESH_HZ
        #self._stimseq_fact = StimulusSequenceFactory(1. / refresh)
        self._stimseq_fact = StimulusSequenceFactory(self._flag)
        self._stimseq_fact.set_view(self._view)

    def _create_view(self):
        return self._view_type()

    def set_iterator_semaphore(self, flag):
        self._flag = flag
        self._iter = lambda it: Switcherator(flag, it)
        self._view.set_iterator_semaphore(flag)
        
    def __setup_events(self):
        handlers = [(pygame.KEYDOWN, self.keyboard_input)]
        self._view.set_event_handlers(handlers)

    def stimulus_sequence(self, prepare, presentation_time):
        """ Returns an object presenting a series of stimuli.
        """
        return self._stimseq_fact.create(prepare, presentation_time,
                                         self.wait_style_fixed)

    def keyboard_input(self, event):
        if event.key == pygame.K_q or event.type == pygame.QUIT:
            self.quit()

    def pre_mainloop(self):
        self._flag.reset()
        try:
            self._view.acquire()
            self.update_parameters()
        except pygame.error, e:
            self.logger.error(e)

    def on_interaction_event(self, data):
        self.update_parameters()

    def update_parameters(self):
        params = dict([[p, getattr(self, p, None)] for p in
                        self._view_parameters])
        self._view.update_parameters(**params)

    def quit(self):
        self.on_stop()
        self._flag.off()
        self._view.quit()

    def post_mainloop(self):
        self._view.close()
