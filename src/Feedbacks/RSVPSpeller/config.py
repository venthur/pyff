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

class Config(object):
    def init(self):
        # 1: Count, 2: YesNo, 3: Calibration, 4: FreeSpelling, 5: CopySpelling
        self.trial_type = 5
        self.alternating_colors = True
        self.sequences_per_trial = 10
        self.geometry = [0, 0, 1280, 1024]
        self.word_font_size = 300
        self.alphabet_font_size = 200
        self.word_target_font_size = 252
        self.word_vpos = 100
        self.alphabet_vpos = 1400
        self.symbol_vpos = 800
        self.symbol_colors = ['red', 'white', 'blue', 'green', 'black']
        self.words = ['LUXUS', 'WINKT', 'FJORD', 'HYBRID', 'SPHINX', 'QUARZ',
                      'VODKA', 'YACHT', 'GEBOT', 'MEMME']
        self.color_groups = ['fRyGk&lt;', 'pJUX!E', 'iSwc-N','TBMqAH','LdvOz.']
        self.nonalpha_trigger = [['-', 57], ['.', 58], ['!', 59], ['<', 60]]
        #self.meaningless = '*+&%?;'
        self.meaningless = ''
        self.custom_pre_sequences = []
        self.custom_post_sequences = []
        # The time for that one single letter is displayed
        self.symbol_duration = .083
        # Pause time directly after each burst
        self.inter_burst = 0
        # Pause time directly after one sequence of bursts or the
        # following user input if set
        self.inter_sequence = 0
        # Pause time directly after one set of sequences for one letter
        # or the following user input if set (count, spelling)
        self.inter_trial = 1
        # Pause time after all targets in one word have been processed
        self.inter_word = .1
        # Display time of a new word in the center
        self.present_word_time = .2
        self.show_trial_fix_cross = True
        self.show_burst_fix_cross = False
        self.show_word_fix_cross = False
        # Display time of the next target in the word
        self.present_target_time = 4
        # Display time of the classifier-selected letter
        self.present_eeg_input_time = 1
        self.key_yes = 'j'
        self.key_no = 'k'
        # What's considered as valid count input discrepancy
        self.max_diff = 20
        self.sound = False
        self.delete_symbol = '<'
        # Display a frame around the current target
        self.show_target_frame = True
        self.target_frame_width = 2
        # Display the current alphabet in corresponding colors at the
        # bottom
        self.show_alphabet = False
        # Allow the eeg input to be simulated by keyboard (for debug)
        self.allow_keyboard_input = True
        # Display the countdown before each new word
        self.show_word_countdown = True
        # Display the countdown before each new target
        self.show_trial_countdown = False
        self.countdown_start = 3
        self.fullscreen = False
        self.headline_vpos = 150
        self.font_color_name = 'black'
        self.bg_color = 'grey'
        self.fixation_cross_time = 3
        self.countdown_symbol_duration = .5
        self._view_parameters += ['symbol_duration', 'present_word_time',
                                  'present_target_time', 'color_groups',
                                  'alternating_colors', 'word_font_size',
                                  'word_target_font_size', 'symbol_colors',
                                  'word_vpos', 'symbol_vpos',
                                  'present_eeg_input_time', 'show_target_frame',
                                  'target_frame_width', 'alphabet_vpos',
                                  'alphabet_font_size', 'show_alphabet']
