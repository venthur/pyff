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

import logging, time

import VisionEgg
import pygame

from FeedbackBase.MainloopFeedback import MainloopFeedback

from lib import marker

from lib.vision_egg.view import VisionEggView
from lib.vision_egg.util.stimulus import StimulusSequenceFactory
from lib.vision_egg.util.switcherator import Flag, Switcherator

VisionEgg.config.VISIONEGG_GUI_INIT = 0
VisionEgg.config.VISIONEGG_LOG_TO_STDERR = 0
VisionEgg.logger.setLevel(logging.ERROR)

class VisionEggFeedback(MainloopFeedback):
    """ Main controlling class for VisionEgg feedbacks. It holds and
    creates the view object, handles keyboard input and provides an
    interface for creating stimulus sequence objects, that ensure
    precise presentation timing.
    The view methods L{add_viewport}, L{add_stimuli} and L{set_stimuli}
    are forwarded for convenience.
    """
    def __init__(self, view_type=VisionEggView, *args, **kwargs):
        """ @param view_type: If a custom view class should be used, its
        type can be specified here. See _create_view for more.
        """
        MainloopFeedback.__init__(self, *args, **kwargs)
        self._view_type = view_type
        self.__init_parameters()
        self.init_parameters()
        self.__init_attributes()

    def __init_parameters(self):
        """ Initialize the pyff parameters. The list _view_parameters
        defines what to pass along to the view object.
        wait_style_fixed: Whether to calculate the presentation time
        of the next stimulus by the previously calculated waiting time
        or the actual real time at the end of the presentation period.
        fullscreen: Run the feedback in fullscreen/window.
        geometry: Upperleft x-pos, y-pos, width, height.
        bg_color: Background color.
        font_color_name: The color used for built-in text, like
        countdown or the center text.
        font_size: Size of the center text.
        fixation_cross_time: How long to display the built-in fixation
        cross when invoked.
        fixation_cross_symbol: What character to display as a fixation
        cross.
        countdown_symbol_duration: How long to display each digit of
        the built-in countdown when invoked.
        countdown_start: First digit of the built-in countdown.
        print_frames: Whether to debug-print the number of frames
        rendered during each stimulus presentation.
        adapt_times_to_refresh_rate: Whether to round off the stimulus
        presentation times to a multiple of the duration of one frame
        of the display device
        framecount_stimulus_transition: Whether to use vsync-determined
        frame counts to assess the stimulus display time
        """
        self.wait_style_fixed = True
        self.fullscreen = False
        self.geometry = [100, 100, 640, 480]
        self.fullscreen_resolution = [1024, 768]
        self.bg_color = 'grey'
        self.font_color_name = 'black'
        self.font_size = 150
        self.fixation_cross_time = .2
        self.fixation_cross_symbol = '+'
        self.countdown_symbol_duration = 1
        self.countdown_start = 5
        self.print_frames = False
        self.adapt_times_to_refresh_rate = True
        self.framecount_stimulus_transition = False
        self._view_parameters = ['fullscreen', 'geometry', 'bg_color',
                                 'font_color_name', 'font_size',
                                 'fixation_cross_time',
                                 'fixation_cross_symbol',
                                 'countdown_symbol_duration',
                                 'countdown_start', 'fullscreen_resolution']

    def init_parameters(self):
        pass

    def __init_attributes(self):
        """ Setup internal attributes. """
        self._view = self._create_view()
        self._view.set_trigger_function(self._trigger)
        self._set_iterator_semaphore(Flag())
        self._running = False
        self.__setup_events()

    def _create_view(self):
        """ Instantiate the view class. Overload this for custom
        parameter specification. """
        return self._view_type()

    def _set_iterator_semaphore(self, flag):
        """ Specify the object to be used as semaphore for iterators.
        See L{Switcherator} for more.
        """
        self._flag = flag
        self._iter = lambda it: Switcherator(flag, it, suspendable=True)
        self._view.set_iterator_semaphore(flag)
        
    def __setup_events(self):
        """ Set L{keyboard_input} to serve as keyboard handler. """
        handlers = [(pygame.KEYDOWN, self.keyboard_input),
                    (pygame.KEYUP, self.keyboard_input_up)]
        self._view.set_event_handlers(handlers)

    def __setup_stim_factory(self):
        """ Create the factory for stimulus sequence handlers. """
        self._stimseq_fact = StimulusSequenceFactory(self._view, self._flag,
                                                     self.print_frames,
                                            self.adapt_times_to_refresh_rate,
                                            self.framecount_stimulus_transition)

    def _trigger(self, trigger, wait=False):
        self.send_parallel(trigger)
        if wait:
            time.sleep(0.03)

    def stimulus_sequence(self, prepare, presentation_time=None,
                          suspendable=True, pre_stimulus_function=None):
        """ Returns an object presenting a series of stimuli.
        @param prepare: This is the core connection between the sequence
        handler and user code. It can either be a generator (so
        presentation continues at a yield statement) or a function
        (continue upon 'return True'. 'return False' terminates the
        presentation sequence). The function should prepare the
        succeeding stimulus.
        @param presentation_time: The duration of presentation of a
        single stimulus, in seconds. Can also be a sequence of values.
        If the prepare function doesn't terminate when the sequence is
        exhausted, it is restarted.
        If the argument is a sequence, any element that is a sequence
        again is used as an interval for random duration selection.
        @param suspendable: Whether the sequence should halt when pause
        is pressed.
        @param pre_stimulus_function: If given, it is called exactly
        before the stimulus transition is made visible. This should not
        be used for preparation or anything time-consuming, so that the
        timing precision won't get compromised.
        """
        return self._stimseq_fact.create(prepare, presentation_time,
                                         self.wait_style_fixed,
                                         suspendable=suspendable,
                                         pre_stimulus=pre_stimulus_function)

    def keyboard_input(self, event):
        """ Handle pygame events like keyboard input. """
        quit_keys = [pygame.K_q, pygame.K_ESCAPE]
        if event.key in quit_keys or event.type == pygame.QUIT:
            self.quit()

    def keyboard_input_up(self, event):
        pass

    def pre_mainloop(self):
        """ Reset the iterator semaphore and initialize the screen. """
        self._flag.reset()
        try:
            self._view.acquire()
            self._update_parameters()
        except pygame.error, e:
            self.logger.error(e)

    def on_interaction_event(self, data):
        if not self._running:
            self._update_parameters()

    def _mainloop(self):
        self._running = True
        self._trigger(marker.RUN_START)
        self.run()
        self._trigger(marker.RUN_END)
        self._running = False
        self.quit()

    def on_pause(self):
        self._flag.toggle_suspension()
        self._trigger(marker.PAUSE_START if self._flag.suspended else
                      marker.PAUSE_END)

    def on_stop(self):
        self.quit()

    def on_quit(self):
        self.quit()

    def _update_parameters(self):
        self.update_parameters()
        """ Apply new parameters set from pyff. """
        params = dict([[p, getattr(self, p, None)] for p in
                        self._view_parameters])
        self.__setup_stim_factory()
        self._view.update_parameters(**params)

    def update_parameters(self):
        pass

    def quit(self):
        self._flag.off()
        self._view.quit()

    def post_mainloop(self):
        self.quit()
        self._view.close()

    def add_viewport(self, viewport):
        """ Add an additional custom viewport object to the list of
        viewports. A viewport is a collection of stimulus objects.
        See http://visionegg.org/reference/VisionEgg.Core.Viewport-class.html
        """
        self._view.add_viewport(viewport)

    def clear_stimuli(self):
        """ Remove all existing stimuli in the standard viewport. """
        self._view.clear_stimuli()

    def add_stimuli(self, *stimuli):
        """ Add a number of stimulus objects to the standard viewport.
        Example:
            txt = Text(text='foo')
            txtr = TextureStimulus(texture=Texture('pic.jpg'))
            self.add_stimuli(txt, txtr)
        The stimulus objects can be any class derived from VisionEgg's
        Core.Stimulus class.
        """
        self._view.add_stimuli(*stimuli)

    def set_stimuli(self, *stimuli):
        """ Set the stimuli of the standard viewport. This removes any
        previously added or set stimuli.
        """
        self._view.set_stimuli(*stimuli)

    def add_text_stimulus(self, text='', font_size=None, **kw):
        """ Create a text object displaying the given text (default
        none) and add it to the standard viewport. The returned object
        is an instance of VisionEgg.Text.Text, whose parameters can be
        changed later using its set() function, which, just as this
        one, takes arbitrary additional parameters listed at
        http://visionegg.org/reference/VisionEgg.Text.Text-class.html
        See also example 1.
        """
        return self._view.add_text_stimulus(text=text, font_size=font_size,
                                            **kw)

    def add_image_stimulus(self, **kw):
        """ Return an image object, a VisionEgg.Textures.TextureStimulus
        instance. calling set_file(filename) on it fills the stimulus
        with the given image.
        Parameters work just as in add_text_stimulus, see
        http://visionegg.org/reference/VisionEgg.Textures.TextureStimul
        us-class.html
        and example 1.
        """
        return self._view.add_image_stimulus(**kw)

    @property
    def screen_size(self):
        """ Convenience property for obtaining the effective size of the
        VisionEgg window.
        """
        return self._view.screen.size
