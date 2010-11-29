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

class Config(object):
    """ This class holds the pyff parameters. The list _view_parameters
    defines what to pass along to the view object.
    """
    def __init__(self):
        self.wait_style_fixed = True
        self.fullscreen = False
        self.geometry = [100, 100, 640, 480]
        self.bg_color = 'grey'
        self.font_color_name = 'green'
        self.font_size = 150
        self.fixation_cross_time = 1.
        self.count_down_symbol_duration = 0.5
        self.count_down_start = 5
        self.print_frames = True
        self._view_parameters = ['fullscreen', 'geometry', 'bg_color',
                                 'font_color_name', 'font_size',
                                 'fixation_cross_time',
                                 'count_down_symbol_duration',
                                 'count_down_start']
