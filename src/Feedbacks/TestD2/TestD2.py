# TestD2.py - Test D2 Implementation for Pyff
# Copyright (C) 2009  Bastian Venthur
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

import random

from FeedbackBase.PygameFeedback import PygameFeedback

# Notation: Letter UpperLines BottomLines
TARGETS = ['d11', 'd20', 'd02']
NON_TARGETS = ['d10', 'd01', 'd21', 'd12', 'd22', 
               'p10', 'p01', 'p11', 'p20', 'p02', 'p21', 'p12', 'p22']

class TestD2(PygameFeedback):

    def init(self):
        PygameFeedback.init(self)
        self.random_seed = 1234
        # Standard D2 configuration
        self.items_per_row = 47
        self.number_of_rows = 14
        self.seconds_per_row = 30
        self.targets_percent = 45.45
        
    def pre_mainloop(self):
        PygameFeedback.pre_mainloop(self)
        self.generate_rows()
        for i in self.rows:
            print i


    def generate_rows(self):
        """Generate the D2 rows."""
        random.seed(self.random_seed)
        targets = round(self.items_per_row * self.targets_percent / 100)
        non_targets = self.items_per_row - targets
        assert(targets+non_targets == self.items_per_row)
        self.rows = []
        for row in range(self.number_of_rows):
            l = [random.choice(TARGETS) for i in range(targets)] + \
                [random.choice(NON_TARGETS) for i in range(non_targets)]
            random.shuffle(l)
            self.rows.append(l)

            

if __name__ == "__main__":
    fb = TestD2()
    fb.on_init()
    fb.on_play()
    