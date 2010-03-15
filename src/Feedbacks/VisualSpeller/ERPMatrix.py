# ERPMatrix.py -
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
#

""" 
Current target triggers range from 11-21, first rows, then columns
11: first row (top)
12: secndon row
13...16
17: first column (left)
18: second column
19...21

Target rows + columns get a value 20 higher than the original value
For instance, for target letter A (first row, first columns), we 
will have the values 31 and 37 (instead of 11 and 17) 

If you use or adapt this software for your research, we would be grateful if you
consider referring to the study for which the speller was developed originally:

Treder, M. S., & Blankertz, B. (C)overt attention and visual speller 
design in an ERP-based brain-computer interface. submitted

"""


import sys, math

import pygame

from FeedbackBase.VisualP300 import VisualP300  # Import P300 superclass 
from lib.P300Layout.MatrixLayout import MatrixLayout # Import spatial layout 
from lib.P300VisualElement.Text import Text # Import Text element for displaying the letters 
from lib.P300VisualElement.Circle import Circle # Import Circle element for displaying a fixation dot
from lib.P300VisualElement.Textrow import Textrow # Import textrow element for displaying the word to-be-copied
from lib.P300Aux.P300Functions import *
from lib.eyetracker import EyeTracker


class ERPMatrix(VisualP300):
    
    # Dimensions of the matrix
    DEFAULT_ROWS = 6
    DEFAULT_COLS = 5
    DEFAULT_MATRIX_WIDTH = 500
    DEFAULT_MATRIX_HEIGHT = 500

    # Pre codes
    PRE_WORD = 0
    PRE_COUNTDOWN = 1
    PRE_WAIT = 2
    PREP_TRIAL = 3

    # Trigger
    START_TRIAL = 100           # Start trial level
    INVALID = 66               # invalid trial
    MATRIX_CENTRAL_FIX = 80# central fixation condition
    MATRIX_TARGET_FIX = 81   # target fixation condition
    
    def init(self):
        VisualP300.init(self)
        # Graphical settings
        self.pygame_info = False
        self.bgcolor = 0, 0, 0
        self.screenWidth, self.screenHeight = 1280, 1024
        self.canvasWidth, self.canvasHeight = 600, 820
        self.fullscreen = True
        # Words
        #self.words = ["WINKT","FJORD","HYBRID","LUXUS","SPHINX","QUARZ","VODKA","YACHT","GEBOT","MEMME"]
        self.words = ["XBCI"]
        self.current_word = 0           # Index of current word
        self.current_letter = 0         # Index of current letter

        # Speller settings
        self.rows = self.DEFAULT_ROWS
        self.cols = self.DEFAULT_COLS
        self.matrix_width = self.DEFAULT_MATRIX_WIDTH 
        self.matrix_height = self.DEFAULT_MATRIX_HEIGHT
        self.letters = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ_,.<")
        self.countdown = 2          # countdown length in seconds
        # Overwritten members of VisualP300
        self.word_time = 50            # How long word is shown (#fps)
        self.word_time_ms = 2500        # word time in ms
        self.min_dist = 2           # Min number of intermediate flashes bef. a flash is repeated twice 
        self.flash_duration = 3
        self.soa = 5
        self.countdown = 4
        self.nr_sequences = 10
        self.trial_nr = 1

        self.fps = 30       
        # Triggers for Level 1 (letter groups) and Level 2 (individual letters)  
        self.matrix_trigger = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        # If a certain group is a target, this value will be added to the trigger  
        self.trigger_target_add = 20
        
        # For data logging (-> the data file is opened in pre_mainloop)
        self.datafilename = "Feedbacks\ERP\data\datafile_matrix.txt"       
        self.datafile = None
        # Eye tracker
        self.use_eyetracker = False
        self.et_fixate_center = True   # Whether center or fixdot has to be fixated   
        self.et_currentxy = (0, 0)      # Current fixation
        self.et_duration = 100
        self.et_targetxy = (0, 0)       # Target coordinates
        self.et_range = 100        # Maximal acceptable distance between target and actual fixation
        self.et_range_time = 200    # maximum acceptable fixation off the designated point 
        #self.et_outside = 0          # Whether current fixation is inside designated area

    def before_mainloop(self):
        """
        Instantiate a matrix layout, add text elements and add 
        groups according to rows and columns. 
        """
        # Get layout & add elements
        self.layout = MatrixLayout(size=(self.matrix_width, self.matrix_height), rows=self.rows, cols=self.cols)
        nr_elements = self.rows * self.cols
        for i in range(nr_elements):
            e = Text(text=self.letters[i], color=(255, 255, 255), size=40)
            e.set_states(0, {"size":40})
            e.set_states(1, {"size":65})
            self.add_element(e)
            e.refresh()
            e.update(0)
        # Determine groups & add them
        rows_cols = self.layout.get_rows_cols()
        for group in rows_cols:
            self.add_group(group)
        # Add fixation dot
        if self.et_fixate_center:
            dot = Circle(radius=3, color=(160, 160, 255))
            dot.pos = (self.screenWidth / 2, self.screenHeight / 2)
            dot.refresh()
            dot.update()
            self.deco.append(dot)
        # Add text row
        self.textrow = Textrow(text="", textsize=42, color=(255, 255, 255), size=(450, 42), edgecolor=(55, 100, 255), antialias=True, colorkey=(0, 0, 0), highlight=[1], highlight_color=(255, 0, 0), highlight_size=62)
        self.textrow.pos = (self.screenWidth / 2, (self.screenHeight - self.canvasHeight) / 2 + 21)
        self.textrow.refresh()
        self.textrow.update()
        self.deco.append(self.textrow)
        # Add count row (where count is entered by participant)
        self.countrow = Textrow(text="", textsize=60, color=(150, 150, 255), size=(100, 60), edgecolor=(255, 255, 255), antialias=True, colorkey=(0, 0, 0))
        self.countrow.pos = (self.screenWidth / 2, self.screenHeight / 2)
        self.countrow.refresh()
        self.countrow.update(0)
        # Add deco to deco group
        if len(self.deco) > 0:
            self.deco_group = pygame.sprite.RenderUpdates(self.deco)
        # Open file for logging data
        if self.datafilename != "":
            try: 
                self.datafile = open(self.datafilename, 'a')
            except IOError:
                print "Cannot open datafile"
                self.datafile = None
                self.on_quit()

        # Sounds
        self.sound_new_word = pygame.mixer.Sound("Feedbacks\ERP-speller\windaVinciSysStart.wav")
        self.sound_countdown = pygame.mixer.Sound("Feedbacks\ERP-speller\winSpaceDefault.wav")
        self.sound_invalid = pygame.mixer.Sound("Feedbacks\ERP-speller\winSpaceCritStop.wav")
        # Variables
        self.group_trigger = None           # Set triggers before each trial
        self.current_word = 0           # Index of current word
        self.current_letter = 0         # Index of current letter
        self.pre_mode = self.PRE_WORD
        self.current_tick = 0
        self.invalid_trial = 0          # Set whether trial is valid or not
        # Send a trigger
        if self.et_fixate_center:
            self.send_parallel(self.MATRIX_CENTRAL_FIX)
        else:
            self.send_parallel(self.MATRIX_TARGET_FIX)
        # Start eye tracker
        self.et = EyeTracker()
        self.et.start()

    
    def pre_trial(self):
        # Countdown,prepare
        if self.pre_mode == self.PRE_WORD: self.new_word()
        elif self.pre_mode == self.PREP_TRIAL: self.prep_trial()
        elif self.pre_mode == self.PRE_COUNTDOWN: self.pre_countdown()
        else: self.wait()
        
    def new_word(self):
        # If we just started a new word: present it
        if self.current_letter == 0 and self.word_time > 0:
            self.sound_new_word.play()
            self.current_tick += 1
            word = self.words[self.current_word]
            font = pygame.font.Font(None, self.textsize)
            self.next_word_image = font.render("Next word: " + word, True, self.textcolor);
            self.next_word_rect = self.next_word_image.get_rect(center=(self.screenWidth / 2, self.screenHeight / 2))
            # Paint it
            self.screen.blit(self.all_background, self.all_background_rect)
            pygame.display.flip()
            self.screen.blit(self.all_background, self.all_background_rect)
            self.screen.blit(self.next_word_image, self.next_word_rect)
            pygame.display.flip()
            pygame.time.wait(self.word_time_ms)

            self.pre_mode = self.PREP_TRIAL
            self.current_tick = 0
            self.current_countdown = 0
        else:
            self.pre_mode = self.PREP_TRIAL
            self.current_tick = 0
            self.current_countdown = 0
            
    def pre_countdown(self):
        if self.countdown > 0:
            if self.current_countdown == 0:
                self.screen.blit(self.all_background, self.all_background_rect)
                self.all_elements_group.draw(self.screen)
                if len(self.deco) > 0: self.deco_group.draw(self.screen)
                pygame.display.flip()
            self.current_countdown += 1
            if self.current_countdown == self.countdown:
                self.pre_mode = self.PRE_WAIT
            self.sound_countdown.play()
            pygame.time.wait(1000)
        else: self.pre_mode = self.PRE_WAIT

            
    def wait(self):
        " Send trigger & wait 1 second"
        self.send_parallel(self.START_TRIAL)
        pygame.time.delay(1000)
        self.state_finished = True

            
    def prep_trial(self):
        # reset variables
        self.invalid_trial = 0
        self.current_countdown = 0
        # get current word
        word = self.words[self.current_word]
        self.textrow.text = word # Set new word
        self.textrow.highlight = [self.current_letter]  # highlight current letter
        self.textrow.refresh()
        # Delete old flash sequence & make new random sequence 
        self.flash_sequence = []
        # Prequel flashes, allowing repetitions
        random_flash_sequence(self, min_dist=self.min_dist, seq_len=11, repetition=True)
        # Experimental sequences
        for i in range(self.nr_sequences):
            random_flash_sequence(self, min_dist=self.min_dist)
        # Sequel, again with repetitions
        random_flash_sequence(self, min_dist=self.min_dist, seq_len=11, repetition=True)
        # Get indices of elements in rows and cols to find target index
        indices = self.layout.get_rows_cols()
        letter = word[self.current_letter]
        ind = self.letters.index(letter)            # Find index of letter
        target_row = 0                              # Two targets: first is row
        target_col = self.rows                      # second is column, starting after the rows
        # Find target row and column
        while ind not in indices[target_row]: target_row += 1  
        while ind not in indices[target_col]: target_col += 1  
        self.group_trigger = self.matrix_trigger[:]
        # Modify trigget of target by adding a value
        self.group_trigger[target_row] += self.trigger_target_add
        self.group_trigger[target_col] += self.trigger_target_add
        # Step to next pre_mode
        self.pre_mode = self.PRE_COUNTDOWN
        # For logfile
        self.datalines = []
        # Flash count
        self.flashcount = 0
        # Determine whether fixate center or fixate target
        if self.et_fixate_center:
            # Fixate center
            self.et_targetxy = (self.screenWidth / 2, self.screenHeight / 2)
        else:
            # Fixate target
            self.et_targetxy = self.elements[ind].pos    
 
    def pre_stimulus(self):
        # Control eye tracker
        if self.use_eyetracker:
            if self.et.x is None:
                self.logger.error("[ERP Matrix] No eyetracker data received!")
                self.on_stop()
                self.state_finished = True
                return
            self.et_currentxy = (self.et.x, self.et.y)
            self.et_duration = self.et.duration
            tx, ty = self.et_targetxy[0], self.et_targetxy[1]
            cx, cy = self.et_currentxy[0], self.et_currentxy[1]
            dist = math.sqrt(math.pow(tx - cx, 2) + math.pow(ty - cy, 2))
            #self.et_outside = 0
            # Check if current fixation is outside the accepted range 
            if dist > self.et_range:
                #self.et_outside = 1
                # Check if the off-fixation is beyond temporal limits
                if self.et_duration > self.et_range_time:
                    self.invalid_trial = 1
                    # Break off current trial !!
                    self.state_finished = True
                    self.sound_invalid.play()
                    show_message(self, "Bad fixation, we have to restart ...")
                    self.screen.blit(self.background, self.background_rect)
                    wait_for_key()
                    # Send break-off trigger
                    self.send_parallel(self.INVALID)
        if self.invalid_trial == 0 and (self.stim_state == self.STIM_START_FLASH) and self.group_trigger is not None:
            self.send_parallel(self.group_trigger[self.flash_sequence[self.current_flash]])
            self.log_data()
            
    def post_trial(self):
        if self.invalid_trial == 1:
            self.current_tick = 0
            self.pre_mode = self.PRE_WORD
            self.state_finished = True
            self.flush_data()
            self.trial_nr += 1
        else:
            # Get count from participant
            self.prompt_count()
            self.flush_data()
            self.trial_nr += 1
            # Check if we reached the final letter
            if self.current_letter == len(self.words[self.current_word]) - 1:
                self.current_letter = 0
                self.current_word += 1
                # Check if we reached the final word
                if self.current_word > len(self.words) - 1:
                    # We reached the end
                    self.on_stop()
            else:
                # Next letter
                self.current_letter += 1
            # Post trial is finished
            self.state_finished = True
            self.current_tick = 0
            self.pre_mode = self.PRE_WORD
            # Give 1 second time
            pygame.time.delay(1000)

    def after_mainloop(self):
        self.sound_new_word = None
        self.sound_countdown = None
        self.sound_invalid = None
        self.countrow = None
        self.textrow = None
        # Stop eyetracker
        self.et.stop()

    def prompt_count(self):
        pygame.event.clear()
        text, ready = "", False
        while not ready:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if k == pygame.K_BACKSPACE:
                        if len(text) > 0: text = text[0: - 1]   # Delete last number
                    elif len(text) < 2:
                        if k == pygame.K_0: text = text + "0"
                        elif k == pygame.K_1: text = text + "1"
                        elif k == pygame.K_2: text = text + "2"
                        elif k == pygame.K_3: text = text + "3"
                        elif k == pygame.K_4: text = text + "4"
                        elif k == pygame.K_5: text = text + "5"
                        elif k == pygame.K_6: text = text + "6"
                        elif k == pygame.K_7: text = text + "7"
                        elif k == pygame.K_8: text = text + "8"
                        elif k == pygame.K_9: text = text + "9"
                    elif k == pygame.K_RETURN: ready = True
            self.countrow.text = text
            self.countrow.refresh()
            self.countrow.update(0)
            self.screen.blit(self.background, self.background_rect)
            self.screen.blit(self.countrow.image, self.countrow.rect)
            pygame.display.flip()
            pygame.time.wait(100)
        self.flashcount = int(text)
            
            
    def log_data(self):
        """
        Structure of logfile
        Word Letter Trial Speller Fix_condition Trigger Time targetx targety currentx currenty Duration FlashCount Invalid(->added at flush)
        """
        #print self.et.x, self.et.y, self.et.duration
        if self.state == self.STIM_START_FLASH:
            word = self.words[self.current_word]
            items = []
            items.append(word)
            items.append(word[self.current_letter])
            items.append(str(self.trial_nr))
            items.append("matrix")
            if self.et_fixate_center:
                items.append("center")
            else:
                items.append("target")
            items.append(str(self.flash_sequence[self.current_flash]))
            items.append(str(pygame.time.get_ticks()))
            if self.use_eyetracker:
                items.append(str(self.et_targetxy[0]))
                items.append(str(self.et_targetxy[1]))
                items.append(str(self.et_currentxy[0]))
                items.append(str(self.et_currentxy[1]))
                items.append(str(self.et_duration))
                #items.append(str(self.et_outside))
            line = "\t".join(items)
            self.datalines.append(line) 
    
    def flush_data(self):
        # Writes the data into the data logfile
        for line in self.datalines:
            line2 = line + "\t" + str(self.flashcount) + "\t" + str(self.invalid_trial) + "\n"
            if self.datafile is not None:
                try: self.datafile.write(line2)
                except IOError:
                    self.logger.warn("Could not write to datafile")


if __name__ == "__main__":
    a = ERPMatrix()
    a.on_init()
    a.on_play()
