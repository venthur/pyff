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
    """Computer version of test D2."""

    def init(self):
        PygameFeedback.init(self)
        self.caption = "Test D2"
        self.random_seed = 1234
        # Standard D2 configuration
        self.number_of_symbols = 47 * 14
        self.seconds_per_symbol = 20 / 47.
        self.targets_percent = 45.45
        # Color of the symbols
        self.color = [0, 0, 0]
        self.backgroundColor = [127, 127, 127]
        # Fontheight in pixels
        self.fontheight = 200
        self.key_target = "f"
        self.key_nontarget = "j"


    def pre_mainloop(self):
        PygameFeedback.pre_mainloop(self)
        self.generate_d2list()
        self.generate_symbols()
        # Initialize the logic
        self.current_index = 0
        # The errors: e1: errors of omission (missing characters that should have been crossed out, 
        #             e2: errors of commission (crossing out characters that shout have not been crossed out
        self.e1 = 0
        self.e2 = 0
        # And here we go...
        pygame.time.set_timer(pygame.QUIT, self.number_of_symbols * self.seconds_per_symbol * 1000)
        self.clock.tick()
        self.present_stimulus()


    def post_mainloop(self):
        elapsed_seconds = self.clock.tick() / 1000.
        PygameFeedback.post_mainloop(self)
        # Total number of items processed
        tn = self.current_index + 1
        error = self.e1 + self.e2
        error_rate = 100. * error / tn
        correctly_processed = tn - error
        # concentration performance := correctly_processed - e2 
        cp = correctly_processed - self.e2
        # Average reaction time:
        rt_avg = elapsed_seconds / tn
        print "Results:"
        print "========"
        print
        print "Processed symbols: %i of %i" % (tn, self.number_of_symbols)
        print "Elapsed time: %f sec" % elapsed_seconds
        print "Correctly processed symbols: %i" % (correctly_processed)
        print "Percentage of Errors: %f" % (error_rate)
        print "Errors:  %i" % error
        print "... errors of omission: %i" % self.e1
        print "... errors of commission: %i" % self.e2
        print "Concentration Performance: %i" % cp
        print "Average reaction time: %f sec" % rt_avg


    def tick(self):
        self.wait_for_pygame_event()
        if self.keypressed:
            key = self.lastkey_unicode
            self.keypressed = False
            if key not in (self.key_target, self.key_nontarget):
                print "Wrong key pressed."
                return
            else:
                print key,
                if key == self.key_nontarget \
                and self.d2list[self.current_index] in TARGETS:
                    print "Wrong (Not recognized D2)"
                    self.e1 += 1
                elif key == self.key_target \
                and self.d2list[self.current_index] in NON_TARGETS:
                    print "Wrong (Confused D2)"
                    self.e2 += 1
                else:
                    print "Correct"
            self.current_index += 1
            if self.current_index > self.number_of_symbols - 1:
                # Finished faster than we expected!
                print "You're awesome dude!"
                self.on_stop()
            else:
                self.present_stimulus()


    def generate_d2list(self):
        """Generate the D2 list."""
        random.seed(self.random_seed)
        # number of targets and non_targets
        targets = int(round(self.number_of_symbols * self.targets_percent / 100))
        non_targets = int(self.number_of_symbols - targets)
        assert(targets + non_targets == self.number_of_symbols)
        l = [random.choice(TARGETS) for i in range(targets)] + \
            [random.choice(NON_TARGETS) for i in range(non_targets)]
        random.shuffle(l)
        # We don't want to have equal symbols in a row, since that can confuse
        # the user when only one symbol is presented
        for i in range(len(l) - 1):
            if l[i] == l[i + 1]:
                pool = TARGETS if l[i] in TARGETS else NON_TARGETS
                new = random.choice(pool)
                while new == l[i + 1]:
                    new = random.choice(pool)
                l[i] = new
        self.d2list = l


    def generate_symbols(self):
        """Generate surfaces all possible symbols."""
        # thickness of the lines (should match thickness of the font
        linewidth = self.fontheight / 11
        font = pygame.font.Font(None, self.fontheight)
        surface_d = font.render("d", True, self.color)
        surface_p = font.render("p", True, self.color)
        # width and height of letters bounding box
        width, height = surface_d.get_size()
        # generate the line surfaces
        surface_l1 = pygame.Surface((width, height), pygame.SRCALPHA)
        surface_l2 = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.line(surface_l1, self.color,
                         (width / 2, height / 10),
                         (width / 2, height - height / 10), linewidth)
        pygame.draw.line(surface_l2, self.color,
                         (width / 3, height / 10),
                         (width / 3, height - height / 10), linewidth)
        pygame.draw.line(surface_l2, self.color,
                         (2 * width / 3, height / 10),
                         (2 * width / 3, height - height / 10), linewidth)
        # Combine letters and lines to the actual symbols and store them in a dict
        self.symbol = {}
        for symbol in TARGETS + NON_TARGETS:
            # Use the Letter...
            surface = pygame.Surface((width, height * 3), pygame.SRCALPHA)
            letter = surface_d if symbol[0] == 'd' else surface_p
            surface.blit(letter, (0, height))
            # ... and attach the lines to it
            if symbol[1] == '1':
                surface.blit(surface_l1, (0, 0))
            elif symbol[1] == '2':
                surface.blit(surface_l2, (0, 0))
            if symbol[2] == '1':
                surface.blit(surface_l1, (0, 2 * height))
            elif symbol[2] == '2':
                surface.blit(surface_l2, (0, 2 * height))
            self.symbol[symbol] = surface


    def present_stimulus(self):
        """Present the current stimulus."""
        print self.d2list[self.current_index]
        self.screen.fill(self.backgroundColor)
        symbol = self.d2list[self.current_index]
        self.screen.blit(self.symbol[symbol], 
                         self.symbol[symbol].get_rect(center=self.screen.get_rect().center))
        pygame.display.flip()


if __name__ == "__main__":
    fb = TestD2()
    fb.on_init()
    fb.on_play()
