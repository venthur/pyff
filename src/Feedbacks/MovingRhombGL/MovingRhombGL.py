
from Feedback import Feedback
import soya


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
        # each point of the rhomb
        points = [( 0.0, -2.0,  0.0),
                  ( 0.0,  0.7,  0.0),
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

        rhomb_world = soya.World()

        soya.Vertex(rhomb_world, *points[0])
        
        color1 = (1,0,0,1)
        color2 = (1,1,1,1)

        i = 0
        for p1, p2, p3 in vertices:
            if i < 4:
                c = color1
            else:
                c = color2
            v1 = soya.Vertex(rhomb_world, *points[p1])
            v2 = soya.Vertex(rhomb_world, *points[p2])
            v3 = soya.Vertex(rhomb_world, *points[p3])
            v1.diffuse = c
            v2.diffuse = c
            v3.diffuse = c

            f = soya.Face(rhomb_world, [v1, v2, v3])
            f.double_sided = 1
            i += 1

                
        self.rhomb_model = rhomb_world.to_model()
        self.rhomb = MovingRotatingBody(self.scene, self.rhomb_model)
        self.rhomb.rotate_z(90)
        self.rhomb.speed = soya.Vector(self.scene, 0.05, 0.1,0)
        
        self.rhomb.rotating = 0
        self.rhomb.angle = 0
    
    def _create_camera_and_light(self):
        self.light = soya.Light(self.scene)
        self.light.set_xyz(5.0, -5.0, 50.0)
        self.light = soya.Light(self.scene)
        self.light.set_xyz(-5.0, -5.0, 5.0)
        self.light = soya.Light(self.scene)
        self.light.set_xyz(5.0, 5.0, 5.0)
        self.light = soya.Light(self.scene)
        self.light.set_xyz(-5.0, 5.0, 5.0)


        
        self.camera =  soya.Camera(self.scene)
        self.camera.z = 15.0
        self.camera.fov = 100
        
        self.camera.ortho = True
        
        p = self.camera.coord2d_to_3d(0.0, 0.0, 0.0)
        print p
        
        soya.set_root_widget(self.camera)
    
    def _run_soya_mainloop(self):
        soya.MainLoop(self.scene).main_loop()

class MovingRotatingBody(soya.Body):
    
    def begin_round(self):
        soya.Body.begin_round(self)
        
        for event in soya.process_event():
            if event[0] == soya.sdlconst.QUIT:
                soya.MAIN_LOOP.stop()
            elif event[0] == soya.sdlconst.KEYDOWN:
                print event
                if not self.rotating:
                    self.rotating = True
                    self.angle = 0.0
                #self.move = True
        
            
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
            self.rotate_y(proportion * 10)
            self.angle += proportion * 10
            if self.angle > 180.0:
                self.rotating = False
                self.rotate_y(180.0 - self.angle)

            
        

if __name__ == '__main__':
    mr = MovingRhombGL(None)
    mr._init_soya()
    mr._create_models()
    mr._create_camera_and_light()
    mr._run_soya_mainloop()
