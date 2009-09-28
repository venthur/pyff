# CircularLayout.py
# Copyright (C) 2009  Matthias Treder
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

"""
Implements a circular layout. All elements are placed on 
a circle with a given radius in pixels. The first element
is placed on the top. The next elements are placed in
clockwise fashion.  

Provide the number of elements (nr_elements) and the radius
(radius) when creating an intance of this layout. You can 
also provide the angular position of the first element (start)
if you do not want it to be placed on the top. 
"""

import math

class CircularLayout(object):
    
    def __init__(self, nr_elements=20, radius=200, start= - math.pi / 2):
        self.positions = []
        step = 2 * math.pi / nr_elements
        for i in range(nr_elements):
            phi = start + i * step
            x = round (radius * math.cos(phi)) 
            y = round (radius * math.sin(phi))
            self.positions.append((x, y))
