#!/usr/bin/env python

# MovingRhomb.py -
# Copyright (C) 2008-2009  Simon Scholler
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

"""MovingRhomb Stimulus."""


import math
import random

import pygame

from FeedbackBase.PygameFeedback import PygameFeedback


class MovingRhomb(PygameFeedback):

    LEFT, RIGHT, TOP, BOTTOM = 1, 2, 3, 4

# From Feedback ################################################################

    def init(self):
        PygameFeedback.init(self)
        self.transparent = (0, 0, 0)
        self.rhomb_bg_color = (255, 255, 255)
        self.rhomb_fg_color = (255, 0, 0)

        self.w, self.h = 800, 600
        self.FPS = 30

        self.angle = 173
        self.duration = 1000.0 # 3s from left to right

        self.random_angle = 5 # degrees

        # TODO: move this to init_graphics
        self.v = (self.w * 1000) / (self.duration * self.FPS)

    def pre_mainloop(self):
        PygameFeedback.pre_mainloop(self)
        self.stopping, self.stop = False, False
        # for now...
        self.rhomb = self.rhomb_left

    def tick(self):
        self.process_pygame_events()
        pygame.time.wait(10)
        self.elapsed = self.clock.tick(self.FPS)

    def play_tick(self):
        self.screen.blit(self.background, self.background.get_rect()) #, self.rhomb_rect)
        # calculate the new position
        speed_v = self.calc_speed_vector(self.v, self.angle)
        self.rhomb_rect.move_ip(speed_v)
        if self.rhomb_rect.left < 0 or self.rhomb_rect.right > self.w:
            self.angle = self.calc_reflection(self.angle, MovingRhomb.LEFT)
            self.angle += 2 * (random.random() - 0.5) * self.random_angle
        if self.rhomb_rect.top < 0 or self.rhomb_rect.bottom > self.h:
            self.angle = self.calc_reflection(self.angle, MovingRhomb.TOP)
            self.angle += 2 * (random.random() - 0.5) * self.random_angle
        # paint it
        self.screen.blit(self.rhomb, self.rhomb_rect)
        # for hwsurfaces and doublebuf
        pygame.display.flip()


# /From Feedback ###############################################################


    def calc_speed_vector(self, v, angle):
        return [v * math.cos(math.radians(angle)), v * math.sin(math.radians(angle))]

    def calc_reflection(self, angle, where):
        rad = math.radians(angle)
        x = math.cos(rad)
        y = math.sin(rad)
        if where in (MovingRhomb.LEFT, MovingRhomb.RIGHT):
            x = -x
        if where in (MovingRhomb.TOP, MovingRhomb.BOTTOM):
            y = -y
        return math.degrees(math.atan2(y, x))


# Pygame Stuff #################################################################
    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """

        # Initialize some usefull variables
        #self.w = self.screen.get_width()
        #self.h = self.screen.get_height()

        # Scale some stuff
        rhomb_w = self.w / 20
        rhomb_h = self.h / 20

        # Paint the Surfaces
        self.background = pygame.Surface((self.w, self.h)).convert()
        self.rhomb_left = pygame.Surface((rhomb_w, rhomb_h)).convert()
        self.rhomb_right = pygame.Surface((rhomb_w, rhomb_h)).convert()
        self.rhomb_up = pygame.Surface((rhomb_w, rhomb_h)).convert()
        self.rhomb_down = pygame.Surface((rhomb_w, rhomb_h)).convert()

        top = (rhomb_w/2, 0)
        left = (rhomb_w, rhomb_h/2)
        bottom = (rhomb_w/2, rhomb_h)
        right = (0, rhomb_h/2)

        rhomb_points = (top, left, bottom, right)
        left_points = (top, bottom, left)
        right_points = (top, right, bottom)
        up_points = (top, right, left)
        down_points = (right, bottom, left)

        self.rhomb_left.set_colorkey(self.transparent)
        pygame.draw.polygon(self.rhomb_left, self.rhomb_bg_color, rhomb_points)
        pygame.draw.polygon(self.rhomb_left, self.rhomb_fg_color, left_points)

        self.rhomb_right.set_colorkey(self.transparent)
        pygame.draw.polygon(self.rhomb_right, self.rhomb_bg_color, rhomb_points)
        pygame.draw.polygon(self.rhomb_right, self.rhomb_fg_color, right_points)

        self.rhomb_up.set_colorkey(self.transparent)
        pygame.draw.polygon(self.rhomb_up, self.rhomb_bg_color, rhomb_points)
        pygame.draw.polygon(self.rhomb_up, self.rhomb_fg_color, up_points)

        self.rhomb_down.set_colorkey(self.transparent)
        pygame.draw.polygon(self.rhomb_down, self.rhomb_bg_color, rhomb_points)
        pygame.draw.polygon(self.rhomb_down, self.rhomb_fg_color, down_points)

        self.rhomb_rect = self.rhomb_left.get_rect(center=self.screen.get_rect().center)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    mr = MovingRhomb()
    mr.on_init()
    mr.on_play()
