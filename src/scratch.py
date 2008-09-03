# scratch.py -
# Copyright (C) 2007-2008  Bastian Venthur
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

import sys, os, os.path, soya

soya.init(fps = 1)
#soya.path.append(os.path.join(os.path.dirname(sys.argv[0]), "soya/data"))
soya.path.append("/home/venthur/soya/data")

scene = soya.World()
pyramid = soya.World()

scene.atmosphere = soya.Atmosphere()
scene.atmosphere.bg_color = (0.05, 0.15, 0.25, 1.0)

# each point of the rhomb
points = [( 0.0, -1.0,  0.0),
          ( 0.0,  1.0,  0.0),
          (-1.0,  0.0, -1.0),
          ( 1.0,  0.0, -1.0),
          ( 1.0,  0.0,  1.0),
          (-1.0,  0.0,  1.0)]

# each vertex has three points
vertices = [(0,2,3),
            (0,3,4),
            (0,4,5),
            (0,5,2),
            (1,2,3),
            (1,3,4),
            (1,4,5),
            (1,5,2)]

soya.Vertex(pyramid, *points[0])

for p1, p2, p3 in vertices:
    f = soya.Face(pyramid, [soya.Vertex(pyramid, *points[p1]),
                        soya.Vertex(pyramid, *points[p2]),
                        soya.Vertex(pyramid, *points[p3])])
    f.double_sided = 1

model_builder = soya.SimpleModelBuilder()
model_builder.shadow = 1
pyramid.model_builder = model_builder

pyramid.shadow = 1

RIGHT = -10.0
LEFT = 10.0
FAR = 10.0
NEAR = -10.0
FLOOR = -2.0

f = soya.Face(scene, [soya.Vertex(scene, RIGHT, FLOOR, FAR),
              soya.Vertex(scene, LEFT, FLOOR, FAR),
              soya.Vertex(scene, LEFT, FLOOR, NEAR),
              soya.Vertex(scene, RIGHT, FLOOR, NEAR)])
f.double_sided = 1

#soya.Face(pyramid, [soya.Vertex(pyramid, -0.5, -0.5,  0.5),
#                                        soya.Vertex(pyramid,  0.5, -0.5,  0.5),
#                                        soya.Vertex(pyramid,  0.0,  0.5,  0.0),
#                                        ])

pyramid.filename = "pyramid"
pyramid.save()

class RotatingBody(soya.Body):
    def advance_time(self, proportion):
        self.rotate_y(2.0 * proportion)
        self.rotate_x(1.0 * proportion)
        self.rotate_z(1.5 * proportion)

p_body = RotatingBody(scene, pyramid.to_model())

#pyramid.rotate_y(60.0)

light = soya.Light(scene)
light.diffuse = 0,0,1,1
light.set_xyz(1.0, 1.7, 1.0)

light2 = soya.Light(scene)
light.diffuse = 0,1,0,1
light2.set_xyz(-2.0, 2.0, 0.0)


camera = soya.Camera(scene)
camera.set_xyz(0.0, 0.0, 3.0)
camera.look_at(pyramid)
soya.set_root_widget(camera)

soya.MainLoop(scene).main_loop()