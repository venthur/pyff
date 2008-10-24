from Feedback import Feedback

import pygame

import math
import random

class MovingRhomb(Feedback):

    LEFT, RIGHT, TOP, BOTTOM = 1, 2, 3, 4

# From Feedback ################################################################

    def on_init(self):
        self.play, self.pause, self.stopping, self.stop = False, False, False, False
        
        self.transparent = (0, 0, 0)
        self.rhomb_bg_color = (255, 255, 255)
        self.rhomb_fg_color = (255, 0, 0)

        self.w, self.h = 1600, 1200
        self.FPS = 60
        
        self.angle = 173
        self.duration = 1000.0 # 3s from left to right

        self.random_angle = 5 # degrees

        # TODO: move this to init_graphics 
        self.v = (self.w * 1000) / (self.duration * self.FPS)
        
    def on_play(self):
        self.init_pygame()
        self.init_graphics()
        self.stopping, self.stop = False, False
        
        # for now...
        self.rhomb = self.rhomb_left
        self.main_loop()
        pygame.quit()
    
    def on_pause(self):
        self.pause = not self.pause
    
    def on_quit(self):
        self.stopping = True
        while not self.stop:
            pass
        #pygame.quit() -- moved to end of on_play in oder to quit it in same thread as it was started
    
# /From Feedback ###############################################################

    def main_loop(self):
        self.clock.tick(self.FPS)
        while not self.stopping:
            self.process_pygame_events()
            
            pygame.time.wait(10)
            self.elapsed = self.clock.tick(self.FPS)
            #print self.elapsed
            self.tick()
        self.stop = True

    def tick(self):
        if self.pause:
            self.pause_tick()
        else:
            self.trial_tick()
            
    def pause_tick(self):
        pass
    
    def trial_tick(self):
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
    def init_pygame(self):
        """
        Set up pygame and the screen and the clock.
        """
        pygame.init()
        #size = (self.w, self.h)
        size = pygame.display.list_modes()[0]
        self.screen = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF) #pygame.HWSURFACE | pygame.FULLSCREEN | pygame.DOUBLEBUF) # 
        self.clock = pygame.time.Clock()
        #print pygame.display.get_driver()
        #print pygame.display.Info()
        #print pygame.display.list_modes()
        
    def init_graphics(self):
        """
        Initialize the surfaces and fonts depending on the screen size.
        """
        
        # Initialize some usefull variables
        self.w = self.screen.get_width()
        self.h = self.screen.get_height()
    
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

        
    def process_pygame_events(self):
        """
        Process the the pygame event queue and react on VIDEORESIZE.
        """
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.init_graphics()
                
if __name__ == '__main__':
    try:
        import threading, time, traceback
        mr = MovingRhomb()
        mr.on_init()

        t = threading.Timer(15, mr.on_quit)
        t.start()
        
        mr.on_play()
    except:
        print traceback.format_exc()
        pygame.quit()

