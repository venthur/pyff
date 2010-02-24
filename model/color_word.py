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

from itertools import izip
from random import uniform
import logging

from AlphaBurst.model.text_list import TextList

class ColorWord(TextList):
    def __init__(self, position, text='', target=None):
        TextList.__init__(self, position)
        self.set(text, target)

    def set(self, text, target):
        self.text = text
        self.clear()
        for l in text:
            size = 96 if l == target else 72
            self.add(l, size)

    def shuffle_colors(self):
        colors = ([uniform(0, 1) for i in xrange(3)] for e in self)
        self.set_colors(colors)

    def set_colors(self, colors):
        for color, symbol in izip(colors, self):
            symbol.set(color=color)
