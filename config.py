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

import string

class Config(object):
    def init(self):
        # 1: Count, 2: YesNo, 3: Calibration, 4: FreeSpelling, 5: CopySpelling
        self.trial_type = 5
        self.alternating_colors = True
        self.sequences_per_trial = 1
        self.fullscreen = False
        self.geometry = [100, 100, 1024, 768]
        self.font_size = 150
        self.headline_font_size = 72
        self.alphabet_font_size = 64
        self.headline_target_font_size = 96
        self.headline_vpos = 100
        self.alphabet_vpos = 1000
        self.symbol_vpos = 300
        self.font_color_name = 'orangered'
        self.symbol_colors = ['red', 'yellow', 'green', 'blue', 'black']
        self.bg_color = 'grey'
        self.words = ['LUXUS', 'WINKT', 'FJORD', 'HYBRID', 'SPHINX', 'QUARZ',
                      'VODKA', 'YACHT', 'GEBOT', 'MEMME']
        self.color_groups = ["ABCEQWFGHI", "KLMNOPDRST", "UVXYJZ.,:<"]
        self.meaningless = '*+&%?;'
        #self.meaningless = ''
        self.custom_pre_sequences = []
        self.custom_post_sequences = []
        # The time for that one single letter is displayed
        self.symbol_duration = .05
        # Pause time directly after each burst
        self.inter_burst = 0
        # Pause time directly after one sequence of bursts or the
        # following user input if set
        self.inter_sequence = .5
        # Pause time directly after one set of sequences for one letter
        # or the following user input if set (count, spelling)
        self.inter_trial = .1
        # Pause time after all targets in one word have been processed
        self.inter_word = .1
        # Display time of a new word in the center
        self.present_word_time = .2
        self.fixation_cross_time = 2.
        self.show_trial_fix_cross = True
        self.show_burst_fix_cross = False
        self.show_word_fix_cross = False
        # Display time of the next target in the headline
        self.present_target_time = .1
        # Display time of the classifier-selected letter
        self.present_eeg_input_time = 1
        self.countdown_start = 5
        self.countdown_symbol_duration = .5
        self.key_yes = 'j'
        self.key_no = 'k'
        # What's considered as valid count input discrepancy
        self.max_diff = 10
        self.sound = False
        self.delete_symbol = '<'
        # Display a frame around the current target
        self.show_target_frame = True
        self.target_frame_width = 2
        # Display the current alphabet in corresponding colors at the
        # bottom
        self.show_alphabet = True
        # Allow the eeg input to be simulated by keyboard (for debug)
        self.allow_keyboard_input = True
        # Display the countdown before each new word
        self.show_word_countdown = True
        # Display the countdown before each new target
        self.show_trial_countdown = False
        self._view_parameters += ['symbol_duration', 'bg_color',
                                  'font_color_name', 'present_word_time',
                                  'present_target_time', 'fixation_cross_time',
                                  'countdown_start',
                                  'countdown_symbol_duration', 'color_groups',
                                  'alternating_colors', 'font_size',
                                  'headline_font_size', 'fullscreen',
                                  'headline_target_font_size', 'geometry',
                                  'symbol_colors', 'headline_vpos',
                                  'symbol_vpos', 'present_eeg_input_time',
                                  'show_target_frame', 'target_frame_width',
                                  'alphabet_vpos', 'alphabet_font_size',
                                  'show_alphabet']
