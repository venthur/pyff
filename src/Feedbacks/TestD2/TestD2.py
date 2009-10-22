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

import pygame

from FeedbackBase.PygameFeedback import PygameFeedback

# Notation: Letter UpperLines BottomLines
TARGETS = ['d11', 'd20', 'd02']
NON_TARGETS = ['d10', 'd01', 'd21', 'd12', 'd22', 
               'p10', 'p01', 'p11', 'p20', 'p02', 'p21', 'p12', 'p22']

class TestD2(PygameFeedback):

    def init(self):
        PygameFeedback.init(self)
        self.caption = "Test D2"
        self.random_seed = 1234
        # Standard D2 configuration
        self.items_per_row = 47
        self.number_of_rows = 14
        self.seconds_per_row = 20
        self.targets_percent = 45.45
        # TODO: use unicode instead of pygame stuff (so we cann remove pygame
        # import in the beginning
        self.key_target = pygame.K_1
        self.key_nontarget = pygame.K_2
        
    def pre_mainloop(self):
        PygameFeedback.pre_mainloop(self)
        self.generate_rows()
        
        self.elapsed_seconds = 0
        self.current_row = 0
        self.current_col = 0
        
    def tick(self):
        PygameFeedback.tick(self)
        self.elapsed_seconds += self.elapsed / 1000.
        if self.elapsed_seconds >= self.seconds_per_row:
            self.elapsed_seconds = 0
            self.current_row += 1
            self.current_col = 0
            # TODO: give short break?
            if self.current_row > self.number_of_rows -1:
                print "Done."
                # TODO: insert final screen and stop feedback.
                self.on_stop()
            print "Next row."
            
        #print self.elapsed_seconds
        if self.keypressed:
            self.keypressed = False 
            if self.lastkey not in (self.key_target, self.key_nontarget):
                print "Wrong key pressed."
                return
            self.current_col += 1
            if self.current_col > self.items_per_row -1:
                print "Done with this row."
            else:
                print self.rows[self.current_row][self.current_col]
        


    def generate_rows(self):
        """Generate the D2 rows."""
        random.seed(self.random_seed)
        targets = int(round(self.items_per_row * self.targets_percent / 100))
        non_targets = int(self.items_per_row - targets)
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
    