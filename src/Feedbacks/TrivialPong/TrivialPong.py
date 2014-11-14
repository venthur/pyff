#!/usr/bin/env python

# TrivialPong.py -
# Copyright (C) 2007-2009  Bastian Venthur
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

"""Trivial Pong BCI Feedback."""


import os

import pygame

from FeedbackBase.PygameFeedback import PygameFeedback


class TrivialPong(PygameFeedback):

    def on_control_event(self, data):
        self.val = data["clout"]

    def init(self):
        PygameFeedback.init(self)
        self.caption = "Trivial Pong"
        # set the initial speeds for ball and bar
        self.barspeed = [3, 0]
        self.speed = [2, 2]
        # set initial value for cl output
        self.val = 0.0

    def init_graphics(self):
        # load graphics
        path = os.path.dirname( globals()["__file__"] )
        self.ball = pygame.image.load(os.path.join(path, "ball.png"))
        self.ballrect = self.ball.get_rect()
        self.bar = pygame.image.load(os.path.join(path, "bar.png"))
        self.barrect = self.bar.get_rect()

    def play_tick(self):
        width, height = self.screenSize
        w_half = width / 2.
        # move bar and ball
        pos = w_half + w_half * self.val
        self.barrect.center = pos, height - 20
        self.ballrect = self.ballrect.move(self.speed)
        # collision detection walls
        if self.ballrect.left < 0 or self.ballrect.right > width:
            self.speed[0] = -self.speed[0]
        if self.ballrect.top < 0 or self.ballrect.bottom > height:
            self.speed[1] = -self.speed[1]
        if self.barrect.left < 0 or self.barrect.right > width:
            self.barspeed[0] = -self.barspeed[0]
        if self.barrect.top < 0 or self.barrect.bottom > height:
            self.barspeed[1] = -self.barspeed[1]
        # collision detection for bar vs ball
        if self.barrect.colliderect(self.ballrect):
            self.speed[0] = -self.speed[0]
            self.speed[1] = -self.speed[1]
        # update the screen
        self.screen.fill(self.backgroundColor)
        self.screen.blit(self.ball, self.ballrect)
        self.screen.blit(self.bar, self.barrect)
        pygame.display.flip()


if __name__ == "__main__":
    fb = TrivialPong()
    fb.on_init()
    fb.on_play()
