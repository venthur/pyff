
from Feedback import Feedback
import soya
import math


class MovingRhombGL(Feedback):
    
    def on_init(self):
        pass
    
    def on_play(self):
        pass
    
    def on_pause(self):
        pass
    
    def on_quit(self):
        pass
    
    def on_control_event(self, data):
        pass
    
    def on_interaction_event(self, data):
        pass

################################################################################

    def _init_soya(self):
        soya.path.append("data")
        soya.init()
        
        self.scene = soya.World()
        
    def _create_models(self):
        leftSize = 2
        rightSize = 0.7
        radius = 1
        n = 8

        color1 = (1,0,0,1)
        color2 = (1,1,1,1)


        rhomb_world = soya.World()


        centerVerticesLeft = []
        centerVerticesRight = []


        for i in range(n):
            l = soya.Vertex(rhomb_world,radius * math.sin(2.0 * math.pi * i / n),0.0, radius * math.cos(2.0 * math.pi * i / n))
            r = soya.Vertex(rhomb_world,radius * math.sin(2.0 * math.pi * i / n),0.0, radius * math.cos(2.0 * math.pi * i / n))
            l.diffuse = color1
            r.diffuse = color2
            centerVerticesLeft.append(l)
            centerVerticesRight.append(r)

        for i in range(n):
            leftVertex = soya.Vertex(rhomb_world, 0.0,-leftSize, 0.0)
            rightVertex = soya.Vertex(rhomb_world, 0.0,rightSize, 0.0)
            leftVertex.diffuse = color1
            rightVertex.diffuse = color2
            f = soya.Face(rhomb_world, [leftVertex, centerVerticesLeft[(i+1)%n], centerVerticesLeft[i]])
            f.smooth_lit = 0
            f = soya.Face(rhomb_world, [rightVertex, centerVerticesRight[i], centerVerticesRight[(i+1)%n]])
            f.smooth_lit = 0

        model_builder = soya.SimpleModelBuilder()

        model_builder.shadow = 1

        rhomb_world.model_builder = model_builder

        self.rhomb_model = rhomb_world.to_model()
        self.rhomb = MovingRotatingBody(self.scene, self.rhomb_model)
        self.rhomb.rotate_z(90)
        self.rhomb.current = RIGHT
        self.rhomb.speed = soya.Vector(self.scene, 0.05, 0.1,0)

        self.rhomb.angle_x = 0
        self.rhomb.angle_y = 0
        self.rhomb.angle_z = 0
        
        self.rhomb.rotating = 0
        self.rhomb.angle = 0
    
    def _create_camera_and_light(self):
        self.light = soya.Light(self.scene)
        self.light.set_xyz(0.0, 0.0, 50.0)


        
        self.camera =  soya.Camera(self.scene)
        self.camera.z = 15.0
        self.camera.fov = 100
        
        self.camera.ortho = True
        
        p = self.camera.coord2d_to_3d(0.0, 0.0, 0.0)
        print p
        
        soya.set_root_widget(self.camera)
    
    def _run_soya_mainloop(self):
        soya.MainLoop(self.scene).main_loop()

# Possible directions of the Body:
NEUTRAL = 0
LEFT    = 1
RIGHT   = 2
UP      = 3
DOWN    = 4

def s(d):
    return {0 : "neutral",
            1 : "left",
            2 : "right",
            3 : "up",
            4 : "down"}[d]

KEY_A = 97
KEY_D = 100
KEY_W = 119
KEY_S = 115
KEY_SPACE = 32

class MovingRotatingBody(soya.Body):
    
    def begin_round(self):
        soya.Body.begin_round(self)
        
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
        
            
        # check where we are and adjust the speed vector if neccessairy
        top = -3.75
        bottom = -top
        
        left = -5.0
        right = -left
        
        if self.x < left or self.x > right:
            self.speed.x = -self.speed.x
            if self.x < left: self.x = left
            elif self.x > right: self.x = right
        
        if self.y < top or self.y > bottom:
            self.speed.y = -self.speed.y
            if self.y < top: self.y = top
            elif self.y > bottom: self.y = bottom

                
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
        print s(self.current), s(proposed)
        self.current = proposed
        

if __name__ == '__main__':
    mr = MovingRhombGL(None)
    mr._init_soya()
    mr._create_models()
    mr._create_camera_and_light()
    mr._run_soya_mainloop()
