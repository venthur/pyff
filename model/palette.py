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

from pygame import Color

class Palette(object):
    def __init__(self):
        self.set(['black'], ['A'])

    def set(self, colors, groups):
        self._alt_colors = colors
        self._color_count = len(colors)
        self._groups = groups

    def __call__(self, color):
        if isinstance(color, list):
            return map(self, color)
        elif isinstance(color, (str, unicode)):
            return self.symbol_color(color) if len(color) == 1 else \
                   Color(color).normalize()
        elif isinstance(color, int):
            return self.alt_color(color)
        else:
            return color

    def alt_color(self, i):
        """ Return a positional color, alternating over alt_colors. """
        return self(self._alt_colors[i % self._color_count])

    def symbol_color(self, symbol):
        index = (i for i, g in enumerate(self._groups) if symbol in g).next()
        return self(index)
