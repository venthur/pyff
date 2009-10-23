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
        # Color of the symbols
        self.color = [0,0,0]
        self.backgroundColor = [155, 155, 155]
        # TODO: use unicode instead of pygame stuff (so we cann remove pygame
        # import in the beginning
        self.key_target = pygame.K_1
        self.key_nontarget = pygame.K_2

        
    def pre_mainloop(self):
        PygameFeedback.pre_mainloop(self)
        self.generate_rows()
        self.generate_symbols()
        # Initialize the logic
        self.elapsed_seconds = 0
        self.current_row = 0
        self.current_col = 0
        # And here we go...
        self.present_stimulus()

        
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
            self.present_stimulus()
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
                self.present_stimulus()


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
            
    
    def generate_symbols(self):
        """Generate surfaces all possible symbols."""
        # Height of the font in pixels
        fontheight = 200
        # thickness of the lines (should match thickness of the font
        linewidth = fontheight / 11
        
        font = pygame.font.Font(None, fontheight)
        surface_d = font.render("d", True, self.color)
        surface_p = font.render("p", True, self.color)
        
        # width and height of letters bounding box
        width, height = surface_d.get_size()

        # generate the line surfaces
        surface_l0 = pygame.Surface( (width, height), pygame.SRCALPHA )
        surface_l1 = pygame.Surface( (width, height), pygame.SRCALPHA )
        surface_l2 = pygame.Surface( (width, height), pygame.SRCALPHA )
        pygame.draw.line(surface_l1, self.color, (width/2, height/10), (width/2, height-height/10), linewidth)
        pygame.draw.line(surface_l2, self.color, (width/3, height/10), (width/3, height-height/10), linewidth)
        pygame.draw.line(surface_l2, self.color, (2*width/3, height/10), (2*width/3, height-height/10), linewidth)

        self.symbol = {}
        for symbol in TARGETS + NON_TARGETS:
            surface = pygame.Surface( (width, height*3), pygame.SRCALPHA )
            letter = surface_d if symbol[0] == 'd' else surface_p
            if int(symbol[1]) == 1: 
                upper = surface_l1
            elif int(symbol[1]) == 2:
                upper = surface_l2
            else:
                upper = surface_l0
            if int(symbol[2]) == 1:
                lower = surface_l1
            elif int(symbol[2]) == 2:
                lower = surface_l2
            else:
                lower = surface_l0
            # blit the stuff an pack it in the dict
            surface.blit(upper, (0, 0))
            surface.blit(letter, (0, height))
            surface.blit(lower, (0, 2*height))
            self.symbol[symbol] = surface


    def present_stimulus(self):
        """Present the current stimulus."""
        print self.rows[self.current_row][self.current_col]
       
        self.screen.fill(self.backgroundColor)
        symbol = self.rows[self.current_row][self.current_col]
        self.screen.blit(self.symbol[symbol], self.symbol[symbol].get_rect(center=self.screen.get_rect().center))
        pygame.display.flip()
            

if __name__ == "__main__":
    fb = TestD2()
    fb.on_init()
    fb.on_play()
    