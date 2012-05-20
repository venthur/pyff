__copyright__ = """ Copyright (c) 2010-2012 Torsten Schmits

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

import numpy

import VisionEgg
import VisionEgg.ParameterTypes as ve_types
import VisionEgg.GL as gl

class Stimulus(object):
    parameters_and_defaults = {}

    def hide(self):
        super(Stimulus, self).set(on=False)

    def show(self):
        super(Stimulus, self).set(on=True)

class TextureStimulus(Stimulus, VisionEgg.Textures.TextureStimulus):
    def set_file(self, name):
        texture = VisionEgg.Textures.Texture(name)
        VisionEgg.Textures.TextureStimulus.set(self, texture=texture)

    def set_height(self, height):
        width, old = self.parameters.texture.size
        self.set(size=(height * width / old, height))

    @property
    def height(self):
        return self.parameters.texture.size[1]

class DisplayListStimulus(VisionEgg.Core.Stimulus):

    def __init__(self, **kw):
        VisionEgg.Core.Stimulus.__init__(self, **kw)
        self._display_list = None

    def draw(self):
        if self._display_list is None:
            self._display_list = gl.glGenLists(1)
            self._generate_list()
        if self.parameters.on:
            gl.glCallList(self._display_list)

    def set(self, *a, **kw):
        VisionEgg.Core.Stimulus.set(self, *a, **kw)
        self._generate_list()

    def _generate_list(self):
        gl.glNewList(self._display_list, gl.GL_COMPILE)
        self._draw()
        gl.glEndList()

    def _draw_vertices(self, *vertices):
        for vertex in vertices:
            gl.glVertex(vertex)

class CircleSector(DisplayListStimulus):
    """  A sector of a circular stimulus, optionally filled.
    

    Parameters
    ==========
    anchor        -- how position parameter is used (String)
                     Default: center
    anti_aliasing -- (Boolean)
                     Default: True
    color         -- color (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    num_triangles -- number of triangles used to draw circle (Integer)
                     Default: 51
    on            -- draw? (Boolean)
                     Default: True
    position      -- position in eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (320.0, 240.0)
    radius        -- radius in eye coordinates (Real)
                     Default: 2.0
    """

    parameters_and_defaults = VisionEgg.ParameterDefinition({
        'on':(True,
              ve_types.Boolean,
              'draw?'),
        'color':((1.0, 1.0, 1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 'color'),
        'color_edge':((1.0, 1.0, 1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 'color for the circle edge'),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        'position' : ( ( 320.0, 240.0 ), # in eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       'position in eye coordinates'),
        'anchor' : ('center',
                    ve_types.String,
                    'how position parameter is used'),
        'radius':(2.0,
                  ve_types.Real,
                  'radius in eye coordinates'),
        'num_triangles':(51,
                         ve_types.Integer,
                         'number of triangles used to draw circle'),
        'start':(0.,
                 ve_types.Real,
                 'start angle'),
        'end':(360.,
                 ve_types.Real,
                 'end angle'),
        'disk':(True,
              ve_types.Boolean,
              'draw the interior?'),
        'circle':(True,
              ve_types.Boolean,
              'draw the edge?'),
        'circle_width':(1.,
                        ve_types.Real,
                        'line width of the circle edge'),
        })
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        '_gave_alpha_warning',
        )

    def __init__(self, **kw):
        DisplayListStimulus.__init__(self, **kw)
        self._gave_alpha_warning = 0

    def _draw(self):
        p = self.parameters
        center = VisionEgg._get_center(p.position, p.anchor, (p.radius, p.radius))
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_BLEND)
        gl.glColor(p.color)
        start, end = p.start, p.end
        if end < start:
            start -= 360.
        start, end = map(numpy.deg2rad, (start, end))
        frac = (end - start) / (2 * numpy.pi)
        num_triangles = float(p.num_triangles) * frac
        angles = numpy.linspace(start, end, num_triangles)
        verts = numpy.zeros((num_triangles, 2))
        verts[:,0] = center[0] + p.radius * numpy.cos(angles)
        verts[:,1] = center[1] + p.radius * numpy.sin(angles)
        if p.disk:
            gl.glBegin(gl.GL_TRIANGLE_FAN)
            gl.glVertex(center)
            self._draw_vertices(*verts)
            gl.glEnd()
            if p.anti_aliasing:
                gl.glEnable(gl.GL_LINE_SMOOTH)
                gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
                gl.glEnable(gl.GL_BLEND)
                # Draw a second polygon in line mode, so the edges are anti-aliased
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                gl.glBegin(gl.GL_TRIANGLE_FAN)
                gl.glVertex(center)
                self._draw_vertices(*verts)
                gl.glEnd()
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                gl.glDisable(gl.GL_LINE_SMOOTH)
        if p.circle:
            if p.anti_aliasing:
                gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glColor(p.color_edge)
            gl.glLineWidth(p.circle_width)
            gl.glBegin(gl.GL_LINES)
            for i in range(verts.shape[0]-1):
                self._draw_vertices(verts[i], verts[i+1])
            gl.glEnd()
            gl.glDisable(gl.GL_LINE_SMOOTH)

class Line(DisplayListStimulus):
    """  A line.
    

    Parameters
    ==========
    anti_aliasing -- (Boolean)
                     Default: True
    color         -- color (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    on            -- draw? (Boolean)
                     Default: True
    position      -- position in eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (320.0, 240.0)
    end           -- position in eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (420.0, 240.0)
    """

    parameters_and_defaults = VisionEgg.ParameterDefinition({
        'on':(True,
              ve_types.Boolean,
              'draw?'),
        'color':((1.0, 1.0, 1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 'color'),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        'position' : ( ( 320.0, 240.0 ), # in eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       'position in eye coordinates'),
        'end' : ( ( 420.0, 240.0 ), # in eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       'end point in eye coordinates'),
        'width':(1.,
                        ve_types.Real,
                        'line width'),
        })
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        '_gave_alpha_warning',
        )

    def __init__(self, **kw):
        DisplayListStimulus.__init__(self, **kw)
        self._gave_alpha_warning = 0

    def _draw(self):
        p = self.parameters
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_BLEND)
        gl.glColor(p.color)
        if p.anti_aliasing:
            gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(p.width)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex(p.position)
        gl.glVertex(p.end)
        gl.glEnd()
        gl.glDisable(gl.GL_LINE_SMOOTH)

class Triangle(DisplayListStimulus):
    """  An equilateral triangle.
    

    Parameters
    ==========
    anti_aliasing -- (Boolean)
                     Default: True
    color         -- color (AnyOf(Sequence3 of Real or Sequence4 of Real))
                     Default: (1.0, 1.0, 1.0)
    on            -- draw? (Boolean)
                     Default: True
    position      -- position in eye coordinates (AnyOf(Sequence2 of Real or Sequence3 of Real or Sequence4 of Real))
                     Default: (320.0, 240.0)
    side          -- side length
    """

    parameters_and_defaults = VisionEgg.ParameterDefinition({
        'anchor' : ('center',
                    ve_types.String,
                    'how position parameter is used'),
        'on':(True,
              ve_types.Boolean,
              'draw?'),
        'color':((1.0, 1.0, 1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 'color'),
        'color_edge':((1.0, 1.0, 1.0),
                 ve_types.AnyOf(ve_types.Sequence3(ve_types.Real),
                                ve_types.Sequence4(ve_types.Real)),
                 'color for the edge'),
        'anti_aliasing':(True,
                         ve_types.Boolean),
        'position' : ( ( 320.0, 240.0 ), # in eye coordinates
                       ve_types.AnyOf(ve_types.Sequence2(ve_types.Real),
                                      ve_types.Sequence3(ve_types.Real),
                                      ve_types.Sequence4(ve_types.Real)),
                       'position in eye coordinates'),
        'side':(10.,
                        ve_types.Real,
                        'side length'),
        'width':(1.,
                        ve_types.Real,
                        'line width'),
        })
    __slots__ = VisionEgg.Core.Stimulus.__slots__ + (
        '_gave_alpha_warning',
        )

    def __init__(self, **kw):
        DisplayListStimulus.__init__(self, **kw)
        self._gave_alpha_warning = 0

    def _draw(self):
        p = self.parameters
        side = p.side
        height = side * numpy.sqrt(3) / 2.
        center = VisionEgg._get_center(p.position, p.anchor, (side, height))
        position = numpy.array(center)
        hh = height / 2
        ll = position - (hh, hh)
        lr = position - (-hh, hh)
        u = position + (0., hh)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_BLEND)
        gl.glColor(p.color)
        gl.glBegin(gl.GL_TRIANGLES)
        self._draw_vertices(ll, lr, u)
        gl.glEnd()
        gl.glColor(p.color_edge)
        if p.anti_aliasing:
            gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(p.width)
        gl.glBegin(gl.GL_LINE_STRIP)
        self._draw_vertices(ll, lr, u, ll)
        gl.glEnd()
        gl.glDisable(gl.GL_LINE_SMOOTH)
