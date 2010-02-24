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

import string

class Config(object):
    def init(self):
        self.tcountdown = 0.
        self.tfixation = 0.
        self.fps = 0.
        self.tstimulus = 0.
        self.symbol_duration = 0.05
        self.IBsI = 0.
        self.ISeI = 0.
        self.IWI = 0.
        self.IBcI = 0.
        self.nsymb = 0.
        self.nsymburst = 0.
        self.nitems = 0.
        self.nburst = 0.
        self.sequences_per_trial = 10
        self.nseq2 = 0.
        self.ntrials = 0.
        self.nblocks = 0.
        self.nwords = 0.
        self.ncol = 0.
        self.font_color = 'orangered'
        self.alternating_colors = True
        self.noccur = 0.
        self.ncount = 0.
        self.fontsize = 0.
        self.fontpos = 0.
        self.bg_color = 'grey'
        self.screen_width = 400
        self.screen_height = 400
        self.fullscreen = False
        self.current_word_index = 0
        self.current_letter_index = 0
        self.sound = False
        self.words = ['WINKT', 'FJORD', 'HYBRID', 'LUXUS', 'SPHINX', 'QUARZ',
                      'VODKA', 'YACHT', 'GEBOT', 'MEMME']
        self.meaningless = '*+&%?;'
        self.target_index = 0
        self.alphabet = string.ascii_uppercase + '.,:<'
        self.burst_duration = 1.
        self.mode = 'ask'
        self._view_parameters = ['symbol_duration', 'bg_color', 'font_color',
                                 'present_word_time', 'present_target_time',
                                 'fixation_cross_time']
        self.key_yes = 'j'
        self.key_no = 'k'
        self.inter_burst = .1
        self.inter_sequence = .5
        self.inter_block = 1.
        self.present_word_time = 2.
        self.fixation_cross_time = 1.
        # color or target letter change
        self.present_target_time = 1.
        self.custom_pre_sequences = [string.ascii_uppercase]
        self.custom_post_sequences = [string.ascii_uppercase]
        self.trial_type = 1
