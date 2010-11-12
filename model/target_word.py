__copyright__ = """ Copyright (c) 2010 Torsten Schmits

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

import operator

from pygame import Color

import VisionEgg.ParameterTypes as ve_types
import VisionEgg.GL as gl
from VisionEgg.Core import Stimulus

from lib.vision_egg.model.color_word import ColorWord

class Frame(Stimulus):
    parameters_and_defaults = {
        'on':(True, ve_types.Boolean),
        'blending_enabled':(False, ve_types.Boolean),
        'depth_test':(False, ve_types.Boolean)
        }

    def __init__(self, position, size, line_width=2, **kw):
        Stimulus.__init__(self, **kw)
        ul = (position[0] - size[0] / 2., position[1])
        add = lambda a, b: map(operator.add, a, b)
        self._vertices = [[ul[0], ul[1], 0],
                          [ul[0] + size[0], ul[1], 0],
                          [ul[0] + size[0], ul[1] + size[1], 0],
                          [ul[0], ul[1] + size[1], 0]]
        self._color = Color('red')
        self._line_width = line_width

    def draw(self):
        p = self.parameters
        if p.on:
            gl.glColor3f(*self._color)
            gl.glDisable(gl.GL_TEXTURE_2D)
            if p.depth_test:
                gl.glEnable(gl.GL_DEPTH_TEST)
            else:
                gl.glDisable(gl.GL_DEPTH_TEST)
            if p.blending_enabled:
                gl.glEnable(gl.GL_BLEND)
            else:
                gl.glDisable(gl.GL_BLEND)
            gl.glLineWidth(self._line_width)
            gl.glBegin(gl.GL_LINE_LOOP)
            for vertex in self._vertices:
                gl.glVertex(*vertex)
            gl.glEnd()

class TargetWord(ColorWord):
    def __init__(self, target_frame=False, target_frame_width=2, **kw):
        self._target_frame = target_frame
        self._target_frame_width = target_frame_width
        ColorWord.__init__(self, **kw)

    def set(self, **kw):
        ColorWord.set(self, **kw)
        self._add_frame()

    def _add_frame(self):
        if self._target_frame and self._target_index is not None:
            current = self[self._target_index]
            pos = current.parameters.position
            size = current.parameters.size
            frame = Frame(pos, size, line_width=self._target_frame_width)
            self.insert(0, frame)
