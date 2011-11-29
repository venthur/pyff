__copyright__ = """ Copyright (c) 2010-2011 Torsten Schmits

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

from VisionEgg import Textures

class Stimulus(object):
    parameters_and_defaults = {}

    def hide(self):
        super(Stimulus, self).set(on=False)

    def show(self):
        super(Stimulus, self).set(on=True)

class TextureStimulus(Stimulus, Textures.TextureStimulus):
    def set_file(self, name):
        texture = Textures.Texture(name)
        Textures.TextureStimulus.set(self, texture=texture)

    def set_height(self, height):
        width, old = self.parameters.texture.size
        self.set(size=(height * width / old, height))
