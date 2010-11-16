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
        self.trial_type = 3
        self.alternating_colors = True
        self.sequences_per_trial = 1
        self.fullscreen = False
        self.geometry = [100, 100, 1024, 768]
        self.font_size = 150
        self.headline_font_size = 72
        self.alphabet_font_size = 64
        self.headline_target_font_size = 96
        self.headline_vpos = 100
        self.alphabet_vpos = 500
        self.symbol_vpos = 300
        self.font_color_name = 'orangered'
        self.symbol_colors = ['red', 'yellow', 'green', 'blue', 'black']
        self.bg_color = 'grey'
        self.words = ['LUXUS', 'WINKT', 'FJORD', 'HYBRID', 'SPHINX', 'QUARZ',
                      'VODKA', 'YACHT', 'GEBOT', 'MEMME']
        self.color_groups = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ.,:<"]
        self.meaningless = '*+&%?;'
        #self.meaningless = ''
        self.custom_pre_sequences = []
        self.custom_post_sequences = []
        self.symbol_duration = .05
        self.inter_burst = 0
        self.inter_sequence = .5
        self.inter_block = .1
        self.inter_trial = .1
        self.present_word_time = .2
        self.fixation_cross_time = 0.
        self.present_target_time = .1
        self.present_eeg_input_time = 1
        self.count_down_start = 0
        self.count_down_symbol_duration = .5
        self.key_yes = 'j'
        self.key_no = 'k'
        self.max_diff = 10
        self.sound = False
        self.current_word_index = 0
        self.current_letter_index = 0
        self.target_index = 0
        self.delete_symbol = '<'
        self.target_frame = True
        self.target_frame_width = 2
        self.show_alphabet = True
        self.allow_keyboard_input = True
        self._view_parameters += ['symbol_duration', 'bg_color',
                                  'font_color_name', 'present_word_time',
                                  'present_target_time', 'fixation_cross_time',
                                  'count_down_start',
                                  'count_down_symbol_duration', 'color_groups',
                                  'alternating_colors', 'font_size',
                                  'headline_font_size', 'fullscreen',
                                  'headline_target_font_size', 'geometry',
                                  'symbol_colors', 'headline_vpos',
                                  'symbol_vpos', 'present_eeg_input_time',
                                  'target_frame', 'target_frame_width',
                                  'alphabet_vpos', 'alphabet_font_size',
                                  'show_alphabet']
