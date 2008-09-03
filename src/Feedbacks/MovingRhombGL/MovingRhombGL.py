
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


    def _init_soya(self):
        soya.path.append("data")
        soya.init()
        
        self.scene = soya.World()
        
    def _create_models(self):
        self.rhomb = Rhomb(self.scene)
        self.rhomb.speed = (1,1,1)
        pass
    
    def _create_camera_and_light(self):
        self.light = soya.Light(self.scene)
        self.light.set_xyz(0.5, 0.0, 2.0)
        
        self.camera =  soya.Camera(self.scene)
        self.camera.z = 2.0
        
        soya.set_root_widget(self.camera)
    
    def _run_soya_mainloop(self):
        soya.MainLoop(self.scene).main_loop()
        
    
class Rhomb(soya.Body):
    
    def begin_round(self):
        soya.Body.begin_round(self)
        
        for event in soya.process_event():
            if event[0] == soya.sdlconst.QUIT:
                soya.MainLoop(self.scene).quit()
            elif event[0] == soya.sdlconst.KEYDOWN:
                print event
                
    def advance_time(self, proportion):
        soya.Body.advance_time(self, proportion)
        self.rotate_x(proportion * 1)
        

if __name__ == '__main__':
    mr = MovingRhombGL(None)
    mr._init_soya()
    mr._create_models()
    mr._create_camera_and_light()
    mr._run_soya_mainloop()
