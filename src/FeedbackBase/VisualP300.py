# VisualP300.py -
# Copyright (C) 2009  Matthias Treder
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
VisualP300 provides a framework for running P300 experiments within pyff.
"""


import sys,os,random
import pygame
from MainloopFeedback import MainloopFeedback
from lib.P300VisualElement.Textbox import Textbox
from lib.P300Aux.P300Functions import wait_for_key,show_message

class VisualP300(MainloopFeedback):
    """
    This class is derived from MainloopFeedback, which provides basic
    functionality.  The class is derived from the Feedback base class and it
    implements a generic visual P300 speller based on the pygame extension
    (http://www.pygame.org). You need to have pygame installed in order to use
    this class or one of its subclasses. Pygame is a simple and easy-to-use 2D
    game engine. For documentation and tutorials, see
    http://www.pygame.org/docs/

    VisualP300 is built in a modular fashion. It is basically a controller
    class which connects a number of components. You can use any combination of
    these predefined components to build your own P300 speller. The components
    are as follows

    layout
        defines the spatial layout of your P300 speller (eg, matrix, circle),
        in other words, it provides the screen coordinates of the elements.
        layout is an instance of one of the P300Layout classes. The README file
        in the P300Layout/ subfolder provides detail information.
    elements
        a list of elements (eg, letters or images). Each element is an instance
        of (a subclass of) P300VisualElement. The README file in the
        P300VisualElement/ subfolder provides detail information.
    deco
        other graphical objects that should be displayed but which are not
        integral parts of the speller (such as a fixation dot)
    groups
        a list of tuples containing the indices of elements that should be
        flashed together (such as rows and columns in the classical P300
        speller)

    **Other important properties**

    group_trigger
        a list with the triggers corresponding to each group.  For a given
        index, the value at that index the triggers are sent via the parallel
        port when a group of elements is flashed. Note that the stimulus method
        automatically sends a trigger with the same index as the current flash
        group.  As an example, if groups[2] is currently flashed, the trigger
        in group_trigger[2] will be sent.  If you want trigger to be different
        depending on whether they correspond to a target or nontarget, you have
        to change group_trigger manually upon each trial.
    flash_sequence
        For the current trial, flash_sequence contains a list of the indices of
        the groups that are flashed subsequently.

    **Timing**

    For convenience, most timing variables (such as flash duration) are given
    in NUMBER OF FRAMES, not in milliseconds. Number of frames is in relation
    to FPS, the actual frames-per-second that is set. You might want change the
    default value to better match your screen refresh rate.

    **Vertical screen refresh**

    It can make a big difference whether or not you use fullscreen mode.  If
    you don't use fullscreen mode, hardware backends may not enable hardware
    surface and double buffering (for more information, see
    http://kevinlocke.name/inquiry/sdlblitspeed/sdlblitspeed.php).  If stimulus
    presentation is not time-locked with the vertical screen refresh rate,
    flickering artefacts may result. Time-locking should be automatically
    enabled in fullscreen mode. If it is not, check

        * if you got the latest graphics driver installed
        * if you got the latest DirectX version (on windows machines)

    You might also need to set your graphics driver to sync vertical refresh
    The standard driver is DirectX. If you work on a non-Windows machine, you
    need to change the video_driver variable
    (ftp://ptah.lnf.kth.se/pub/misc/sdl-env-vars gives a list of drivers).
    Double buffering is enabled by default to prevent tearing. Note that with
    doublebuf, hwsurface (hardware surface) is used instead of swsurface
    (software surface).  If you write your own drawing routines, be sure to use
    pygame.diplay.flip() command instead of pygame.display.update(), to have
    your stimuli rendered properly in double buffer mode.

    To prepare your own experiment, you could first have a look at the examples
    such as P300Matrix.py and P300Hex.py
    """


    DEFAULT_SCREEN_WIDTH,DEFAULT_SCREEN_HEIGHT = 800,800
    DEFAULT_FULLSCREEN = False
    DEFAULT_BGCOLOR = 0,0,0                 # Default background color

    # Give durations as number of frames
    DEFAULT_FLASH_DURATION = 5
    DEFAULT_SOA = 10                        # Time between the onset of two flashes (stimlus onset asynchrony)
    DEFAULT_FPS = 60                        # Default frames per second

#    """ If state_change is set to true, state changes (ie, OFF-ON or ON-OFF)
#        will be presented instead of flashes (ie, OFF-ON-OFF) """
#    DEFAULT_STATE_CHANGE = False            # Set here whether you want state changes (OFF-ON or ON-OFF) or flashes (OFF-ON-OFF)
    DEFAULT_NR_SEQUENCES = 1            # nr of times each group is flashed in a trial

    # Settings for textmessages via the function show_message()
    DEFAULT_TEXTSIZE = 40
    DEFAULT_TEXTCOLOR = 255,255,255

    # Settings for pygame
    DEFAULT_PYGAME_INFO = True                # If true, gives a screen with information about pygame settings
    #DEFAULT_VIDEO_DRIVER = 'directx'

    # Speller states
    PRE_TRIAL = 0
    STIMULUS = 1
    FEEDBACK = 2
    POST_TRIAL = 3

    # Stimulus states
    STIM_START_FLASH = 1
    STIM_IN_FLASH = 2
    STIM_END_FLASH = 3
    STIM_BETWEEN_FLASHES = 4

    # *** Overwritten MainloopFeedback methods ***
    def init(self):
        """Define your variables here."""
        # Visual settings
        self.window_title = "Visual P300"
        self.screenWidth,self.screenHeight = self.DEFAULT_SCREEN_WIDTH,self.DEFAULT_SCREEN_HEIGHT
        """ Canvas: The part of the screen which is used for painting!
        That's more efficient than repainting the whole of the screen
        """
        self.canvasWidth,self.canvasHeight = 600,600
        self.fullscreen = self.DEFAULT_FULLSCREEN
        self.bgcolor = self.DEFAULT_BGCOLOR
        self.textsize = self.DEFAULT_TEXTSIZE
        self.textcolor = self.DEFAULT_TEXTCOLOR
        # Trigger
        self.group_trigger = None   # Triggers are specified in the subclass
        # Data logging
        self.datafile = None            # If a string is provided, logging is enabled
        # Timing
        self.flash_duration= self.DEFAULT_FLASH_DURATION
        self.soa = self.DEFAULT_SOA
        self.nr_sequences = self.DEFAULT_NR_SEQUENCES
        #self.state_change = self.DEFAULT_STATE_CHANGE
        self.fps = self.DEFAULT_FPS
        # Random number generator
        self.random = random.Random()           # Get random generator

        # pygame specific variables
        self.pygame_info = self.DEFAULT_PYGAME_INFO
#        self.video_driver = self.DEFAULT_VIDEO_DRIVER

    def pre_mainloop(self):
        """
        - define a layout
        - define your visual elements and add them to the elements list
          using the add_element method
        - define your deco and add them to the deco list
        - make a deco_group containing all deco
        - define your groups and add them to the groups list
          using the add_group method
        - define your triggers

        Always create a layout before you add elements, and add elements
        before you add groups.
        """
        self.current_flash = 0                  # Index of the flash presented last
        # Core members
        self.layout = None          # layout is specified in the subclass
        self.elements = []          # elements are specified in the subclass
        self.deco = []              # decoration (elements such as frames, text fields, etc, that are not an integral part of the P300 speller)
        self.groups = []            # specifies which elements are flashed together
        self.deco_group = None
        # Speller state
        self.state = self.PRE_TRIAL
        self.state_finished = False
        self.flash_sequence = []
        self.nr_flashes = None                  # len of flash sequence
        # Stimulus states
        self.stim_state = None
        # Init pygame and start before_mainloop implemented by children
        self._init_pygame()
        self.before_mainloop()

    def before_mainloop(self):
        """
        Prepare your elements, groups, triggers etc in this method
        """
        pass

    def _init_pygame(self):
        # Initialize pygame, open screen and fill screen with background color
        #os.environ['SDL_VIDEODRIVER'] = self.video_driver   # Set video driver
        pygame.init()
        if self.fullscreen:
            #use opts = pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN to use doublebuffer and vertical sync
            opts = pygame.FULLSCREEN
            self.screen = pygame.display.set_mode((self.screenWidth,self.screenHeight),opts)
        else:
            self.screen = pygame.display.set_mode((self.screenWidth,self.screenHeight))
        self.background = pygame.Surface( (self.canvasWidth,self.canvasHeight) )
        self.background.fill(self.bgcolor)
        self.background_rect = self.background.get_rect(center = (self.screenWidth/2,self.screenHeight/2) )
        # Background for whole screen (needs lots of time to paint, use self.background in most cases)
        self.all_background = pygame.Surface( (self.screenWidth,self.screenHeight) )
        self.all_background.fill(self.bgcolor)
        self.all_background_rect = self.all_background.get_rect(center = (self.screenWidth/2,self.screenHeight/2) )
        self.screen.blit(self.all_background,self.all_background_rect)
        pygame.display.flip()
        self.screen.blit(self.all_background,self.all_background_rect)
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)
        # init sound engine
        pygame.mixer.init()
        if self.pygame_info:        # If true, give some information
            inf = pygame.display.Info()
            driver = pygame.display.get_driver()
            text = "PYGAME SYSTEM INFO\n\n"
            text += "Display driver: "+str(driver)+"\nFullscreen: "+str(self.fullscreen)
            text += "\nhw: "+str(inf.hw)+"\nwm: "+str(inf.wm)
            text += "\nvideo_mem: "+str(inf.video_mem) +"\nbytesize: "+str(inf.bytesize)
            text += "\nblit_hw: "+str(inf.blit_hw) +"\nblit_hw_CC: "+str(inf.blit_hw_CC)+"\nblit_hw_A: "+str(inf.blit_hw_A)
            text += "\nblit_sw: "+str(inf.blit_sw) +"\nblit_sw_CC: "+str(inf.blit_sw_CC)+"\nblit_sw_A: "+str(inf.blit_sw_A)
            show_message(self,text,box=True)
            wait_for_key()


    def post_mainloop(self):
        """
        save your log file etc
        """
        self.after_mainloop()
        # Get rid of  pygame objects
        self.clock = None
        self.background = None
        self.background_rect = None
        self.all_background = None
        self.all_background_rect = None
        self.groups = None
        self.all_elements_group = None
        self.deco_group = None
        self.deco = None
        self.elements = None
        self.screen = None
        pygame.quit()
        # Close datafile
        if self.datafile is not None:
            try: self.datafile.close()
            except IOError: self.logger.warn("Could not close datafile")

    def after_mainloop(self):
        """ Put here any 'cleaning-up' you want to do after the experiment
        You should also clean up all references to pygame objects here, e.g.
        by deleting the reference or setting it to None (or any other non-
        pygame object)
        """
        pass

    def tick(self):
        # Check event cue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.on_stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.on_stop()
        # If last state is finished, proceed to next state
        if self.state_finished:
            if self.state == self.PRE_TRIAL:
                self.state = self.STIMULUS
            elif self.state == self.STIMULUS:
                self.state  = self.FEEDBACK
            elif self.state == self.FEEDBACK:
                self.state = self.POST_TRIAL
            elif self.state == self.POST_TRIAL:
                self.state = self.PRE_TRIAL
            self.state_finished = False

    def pause_tick(self):
        pygame.time.wait(100)

    def play_tick(self):
        state = self.state
        if state == self.PRE_TRIAL:
            self._pre_trial()
        elif state == self.STIMULUS:
            self.pre_stimulus()
            if not self.state_finished:
                self._stimulus()
            self.post_stimulus()
        elif state == self.FEEDBACK:
            self.feedback()
        elif state == self.POST_TRIAL:
            self._post_trial()

    def _pre_trial(self):
        self.pre_trial()
        # Make a group containing all current elements
        self.all_elements_group = pygame.sprite.RenderUpdates(self.elements)
        self.all_elements_group.update(0)
        self.all_elements_group.draw(self.screen)
        """ In order for the group.clear method (called in the flashing loop)
        to work, the group.draw methods have to have been called before, """
        for i in range(len(self.groups)):
            self.groups[i].draw(self.screen)  # Initialize first group
        self.current_flash = 0
        self.nr_flashes = len(self.flash_sequence)
        self.stim_state = self.STIM_START_FLASH

    def pre_trial(self):
        """
        choose stimulus, define the triggers, target, and perform any
        other computations necessary to perform the stimulus. You can also
        display text messages before the start of the trial and present a
        countdown

        You should overwrite this method to prepare your flash_sequence and
        graphics here, if necessary. You have to set  self.state_finished = True
        to proceed to the next state.
        """
        self.state_finished = True

    def pre_stimulus(self):
        # logging, send trigger, check eye tracker
        pass

    def _stimulus(self):
        """
        Here, the stimulus is presented. Usually, you will not need to
        override this method
        """
        state = self.stim_state
        if state == self.STIM_IN_FLASH:
            # Wait flash time
            self.current_tick += 1
            if self.current_tick == self.flash_duration:
                self.stim_state = self.STIM_END_FLASH
        elif state == self.STIM_START_FLASH:
            # Flash ON
            self.groups[self.flash_sequence[self.current_flash]].update()      # change state
            self.current_tick = 0
            if self.flash_duration > 1:
                self.stim_state = self.STIM_IN_FLASH
            else: self.stim_state = self.STIM_END_FLASH
            # We only need to paint if smth changes
            self.screen.blit(self.background,self.background_rect)
            self.all_elements_group.draw(self.screen)
            if len(self.deco)>0: self.deco_group.draw(self.screen)
            pygame.display.flip()
        elif state == self.STIM_END_FLASH:
            # Flash OFF
            self.groups[self.flash_sequence[self.current_flash]].update(-1)      # change state back
            self.current_tick += 1
            if self.current_tick+1 < self.soa:
                self.stim_state = self.STIM_BETWEEN_FLASHES
            else:
                self.stim_state = self.STIM_START_FLASH
            self.current_flash += 1
            if self.current_flash == self.nr_flashes:
                self.state_finished = True      # All flashes have been shown
                self.current_tick = 0           # Reset current tick
            self.screen.blit(self.background,self.background_rect)
            self.all_elements_group.draw(self.screen)
            if len(self.deco)>0: self.deco_group.draw(self.screen)
            pygame.display.flip()
        elif state == self.STIM_BETWEEN_FLASHES:
            self.current_tick += 1
            if self.current_tick == self.soa:
                self.current_tick = 0
                self.stim_state = self.STIM_START_FLASH
        self.clock.tick(self.fps)

    def post_stimulus(self):
        # logging, send trigger, check eye tracker
        pass

    def feedback(self):
        """ Present feedback (for instance the chosen letter)
        """
        # Give your feedback (eg the chosen symbol) here
        self.state_finished = True

    def _post_trial(self):
        # Do not overwrite this method
        self.post_trial()

    def post_trial(self):
        """
        any clean up

        Any stuff you need to do after presenting a trial.
        You have to set  self.state_finished = True to proceed
        to the next state.
        """
        self.state_finished = True

    def add_element(self,element):
        """
        Adds a visual element to the list of elements and set
        it on the position specified by the layout
        """
        nr_elements = len(self.elements)     # Number of elements already in list
        if self.layout is None:
            self.logger.warn("Cannot add element: no layout specified")
        else:
            # Position element so that it's centered on the screen
            (x,y) = self.layout.positions[nr_elements]
            element.pos = (x+self.screenWidth/2,y+self.screenHeight/2)
            self.elements.append(element)

    def add_group(self,group):
        """
        Takes the indices of the elements in the elements list and
        adds them as one group
        """
        new_group = pygame.sprite.RenderUpdates()
        if type(group) == int:
            new_group.add(self.elements[group])
        else:
            for g in group:
                new_group.add(self.elements[g])
        self.groups.append(new_group)

    def log_data(self):
         """
         Overwrite this method to log your specific data. The datafile object
         is referenced by self.datafile. You should open the file yourself
         in the pre_mainloop  method of your derived class. The file is closed
         automatically when the feedback is stopped.
         """
         pass
