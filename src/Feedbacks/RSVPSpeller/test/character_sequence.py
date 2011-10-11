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

from string import ascii_uppercase
from unittest import TestCase

from Feedbacks.RSVPSpeller.model.character_sequence import CharacterSequenceFactory
from Feedbacks.RSVPSpeller.model.palette import Palette

class CharacterSequenceTest(TestCase):
    def test_color(self):
        symbol_colors = ['red', 'yellow', 'green', 'blue', 'black']
        color_groups = ["ABCDEFGHIJ", "KLMNOPQRST", "UVWXYZ.,:<"]
        palette = Palette()
        palette.set(symbol_colors, color_groups)
        factory = CharacterSequenceFactory('!@#$%^?', True, 'E', palette)
        s = factory.sequences(4, [], [])
        print [seq.burst_sequence for seq in s]
