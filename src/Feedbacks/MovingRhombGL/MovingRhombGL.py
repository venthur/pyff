# MovingRhombGL.py - MovingRhomb implementation in OpenGL using Soya 3D
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

"""Stimulus-Only Feedback."""


import math
import time

import soya

from FeedbackBase.Feedback import Feedback


class MovingRhombGL(Feedback):
    
    def on_init(self):
        # for the rhomb
        self.rhomb_left_size = 2.0
        self.rhomb_right_size = 0.7
        self.rhomb_radius = 1.0
        self.rhomb_n = 16
        self.rhomb_color1 = (1,0,0,1)
        self.rhomb_color2 = (1,1,1,1)
        self.rhomb_speed_xyz = (0.05, 0.1,0)
        
        # camera and light
        self.light_xyz = (0,0,50)
        self.camera_z = 15
        self.camera_fov = 100

    
    def on_play(self):
        self._init_soya()
        self._create_models()
        self._create_camera_and_light()
        
        # this method will run until stopped from another thread
        self.rhomb.stopping = False
        self._stopped = False
        self._run_soya_mainloop()
        
        soya.quit()
        print "Stopped soya's main loop."
        self._stopped = True
    
    def on_pause(self):
        self._pause = not self._pause
    
    def on_quit(self):
        self.rhomb.stopping = True
        while not self._stopped:
            time.sleep(0.1)
    

################################################################################

    def _init_soya(self):
        soya.path.append("data")
        soya.init()
        self.scene = soya.World()

        
    def _create_models(self):
        rhomb_world = soya.World()
        centerVerticesLeft = []
        centerVerticesRight = []
        for i in range(self.rhomb_n):
            l = soya.Vertex(rhomb_world,self.rhomb_radius * math.sin(2.0 * math.pi * i / self.rhomb_n),0.0, self.rhomb_radius * math.cos(2.0 * math.pi * i / self.rhomb_n))
            r = soya.Vertex(rhomb_world,self.rhomb_radius * math.sin(2.0 * math.pi * i / self.rhomb_n),0.0, self.rhomb_radius * math.cos(2.0 * math.pi * i / self.rhomb_n))
            l.diffuse = self.rhomb_color1
            r.diffuse = self.rhomb_color2
            centerVerticesLeft.append(l)
            centerVerticesRight.append(r)
        for i in range(self.rhomb_n):
            leftVertex = soya.Vertex(rhomb_world, 0.0,-self.rhomb_left_size, 0.0)
            rightVertex = soya.Vertex(rhomb_world, 0.0,self.rhomb_right_size, 0.0)
            leftVertex.diffuse = self.rhomb_color1
            rightVertex.diffuse = self.rhomb_color2
            f = soya.Face(rhomb_world, [leftVertex, centerVerticesLeft[(i+1)%self.rhomb_n], centerVerticesLeft[i]])
            f.smooth_lit = 1
            f = soya.Face(rhomb_world, [rightVertex, centerVerticesRight[i], centerVerticesRight[(i+1)%self.rhomb_n]])
            f.smooth_lit = 1
        model_builder = soya.SimpleModelBuilder()
        model_builder.shadow = 1
        rhomb_world.model_builder = model_builder

        self.rhomb_model = rhomb_world.to_model()
        self.rhomb = MovingRotatingBody(self.scene, self.rhomb_model)
        self.rhomb.rotate_z(90)
        self.rhomb.current = RIGHT
        self.rhomb.speed = soya.Vector(self.scene, *self.rhomb_speed_xyz)

        self.rhomb.angle_x = 0
        self.rhomb.angle_y = 0
        self.rhomb.angle_z = 0
        
        self.rhomb.rotating = 0
        self.rhomb.angle = 0

    
    def _create_camera_and_light(self):
        self.light = soya.Light(self.scene)
        self.light.set_xyz(*self.light_xyz)
        
        self.camera =  soya.Camera(self.scene)
        self.camera.z = self.camera_z
        self.camera.fov = self.camera_fov
        self.camera.ortho = True
        
        # calculate the "border" of the field
        p = self.camera.coord2d_to_3d(0.0, 0.0, 0.0)
        self.rhomb.left = p.x
        self.rhomb.right = -p.x
        self.rhomb.top = p.y
        self.rhomb.bottom = -p.y
        
        soya.set_root_widget(self.camera)

    
    def _run_soya_mainloop(self):
        soya.MainLoop(self.scene).main_loop()


# Possible directions of the Body:
NEUTRAL = 0
LEFT    = 1
RIGHT   = 2
UP      = 3
DOWN    = 4

# Scancodes for the Keys
KEY_A = 97
KEY_D = 100
KEY_W = 119
KEY_S = 115
KEY_SPACE = 32

class MovingRotatingBody(soya.Body):
    
    def begin_round(self):
        soya.Body.begin_round(self)
        if self.stopping:
            soya.MAIN_LOOP.stop()
        
        for event in soya.process_event():
            if event[0] == soya.sdlconst.QUIT:
                soya.MAIN_LOOP.stop()
            elif event[0] == soya.sdlconst.KEYDOWN:
                direction = {KEY_A : LEFT,
                             KEY_D : RIGHT,
                             KEY_W : UP,
                             KEY_S : DOWN,
                             KEY_SPACE : NEUTRAL}.get(event[1], NEUTRAL)
                if not self.rotating: 
                    self.turn_to(direction)
                
#                if not self.rotating:
#                    self.rotating = True
#                    self.angle = 0.0
#                #self.move = True
            
        # check where we are and adjust the speed vector and position if 
        # neccessairy
        if self.x < self.left or self.x > self.right:
            self.speed.x = -self.speed.x
            if self.x < self.left: self.x = self.left
            elif self.x > self.right: self.x = self.right
        if self.y < self.bottom or self.y > self.top:
            self.speed.y = -self.speed.y
            if self.y < self.bottom: self.y = self.bottom
            elif self.y > self.top: self.y = self.top

                
    def advance_time(self, proportion):
        soya.Body.advance_time(self, proportion)
        #if self.move:
        #    self.add_mul_vector(proportion, self.speed)
        self.add_mul_vector(proportion, self.speed)
        
        
        
        if self.rotating:
            #self.rotate_y(proportion * 10)
            #self.angle += proportion * 10
            #if self.angle > 180.0:
            #    self.rotating = False
            #    self.rotate_y(180.0 - self.angle)
            #    print self.direction
            
            self.rotate_x(proportion * self.angle_x)
            self.rotate_y(proportion * self.angle_y)
            self.rotate_z(proportion * self.angle_z)
            
    
    def end_round(self):
        self.rotating = False
                
    def turn_to(self, direction=NEUTRAL):
        """Turns the body to the given scene direction.
        
        If no direction is given, it defaults to neutral position."""
        

        current = self.current
        proposed = direction
        
        xyz = [0,0,0]    
        if current == NEUTRAL:
            if proposed == NEUTRAL:
                xyz = [0.0, 0.0, 0.0]
            elif proposed == UP:
                xyz = [90.0, 0.0, 0.0]
            elif proposed == DOWN:
                xyz = [-90.0, 0.0, 0.0]
            elif proposed == LEFT:
                xyz = [0.0, 90.0, 0.0]
            elif proposed == RIGHT:
                xyz = [0.0, -90.0, 0.0]
        elif current == UP:
            if proposed == NEUTRAL:
                xyz = [-90.0, 0.0, 0.0]
            elif proposed == UP:
                xyz = [0.0, 0.0, 0.0]
            elif proposed == DOWN:
                xyz = [180.0, 0.0, 0.0]
            elif proposed == LEFT:
                xyz = [0.0, 0.0, 90.0]
            elif proposed == RIGHT:
                xyz = [0.0, 0.0, -90.0]
        elif current == DOWN:
            if proposed == NEUTRAL:
                xyz = [90.0, 0.0, 0.0]
            elif proposed == UP:
                xyz = [180.0, 0.0, 0.0]
            elif proposed == DOWN:
                xyz = [0.0, 0.0, 0.0]
            elif proposed == LEFT:
                xyz = [0.0, 0.0, -90.0]
            elif proposed == RIGHT:
                xyz = [0.0, 0.0, 90.0]
        elif current == LEFT:
            if proposed == NEUTRAL:
                xyz = [0.0, -90.0, 0.0]
            elif proposed == UP:
                xyz = [0.0, 0.0, -90.0]
            elif proposed == DOWN:
                xyz = [0.0, 0.0, 90.0]
            elif proposed == LEFT:
                xyz = [0.0, 0.0, 0.0]
            elif proposed == RIGHT:
                xyz = [0.0, 180.0, 0.0]
        elif current == RIGHT:
            if proposed == NEUTRAL:
                xyz = [0.0, 90.0, 0.0]
            elif proposed == UP:
                xyz = [0.0, 0.0, 90.0]
            elif proposed == DOWN:
                xyz = [0.0, 0.0, -90.0]
            elif proposed == LEFT:
                xyz = [0.0, 180.0, 0.0]
            elif proposed == RIGHT:
                xyz = [0.0, 0.0, 0.0]
        # begin rotating
        
        self.rotating = True
        self.angle_x, self.angle_y, self.angle_z = xyz
        self.current = proposed
        

if __name__ == '__main__':
    mr = MovingRhombGL()
    mr.on_init()
    mr._init_soya()
    mr._create_models()
    mr._create_camera_and_light()
    mr._run_soya_mainloop()
