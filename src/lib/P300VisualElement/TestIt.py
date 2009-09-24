# TestIt.py
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
Use TestIt to test your new visual elements. 
Test it opens a test screen, displays the element and goes through
its states. 
"""

    
import sys

import pygame

import Textrow


bgcolor = 0, 0, 0
screenSize = 500, 500

""" Import & define your element here"""
#import Hexagon,math
#e = Hexagon.Hexagon(color=(255,255,255),radius=60,text="ABCD",edgecolor=(255,255,255),textcolor=(10,10,100),textsize=10,colorkey=(0,0,0),antialias=True)

text = "LUXUS"



""" Init pygame, open screen etc """
pygame.init()
screen = pygame.display.set_mode(screenSize)
background = pygame.Surface(screenSize) 
background.fill(bgcolor)
screen.blit(background, [0, 0])
pygame.display.update()

""" Loop between the states and pause in between """
width, height = screenSize
e.pos = (width / 2, height / 2)
e.refresh()
e.update(0)
pos = 0
while 1:
    screen.blit(background, [0, 0])
    screen.blit(e.image, e.rect)
    pygame.display.flip()
    e.update()
    pygame.time.delay(400)
    e.highlight = [pos]
    e.refresh()
    pos = (pos + 1) % len(text)
    for event in pygame.event.get():
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            sys.exit(0)
            break
            