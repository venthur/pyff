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

alt_color = [Color('red'), Color('yellow'), Color('blue')]

def color(i):
    """ Return a positional color, alternating over alt_color.

    """
    return alt_color[i % len(alt_color)].normalize()

def symbol_color(symbol, groups):
    index = (i for i, g in enumerate(groups) if symbol in g).next()
    return color(index)
