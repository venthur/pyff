#!/usr/bin/env python

import pygame

from FeedbackBase.EventDrivenFeedback import EventDrivenFeedback

class TestEventDrivenFeedback(EventDrivenFeedback):


    def run(self):
        pygame.init()
        pygame.display.set_mode([800, 600], pygame.HWSURFACE)
        # Glue pygame events to ours
        self.bind_event_to_method(pygame.VIDEOEXPOSE, self.paint)
        self.bind_event_to_method(pygame.KEYDOWN, self.keyboard)
        self.bind_event_to_method(pygame.MOUSEBUTTONDOWN, self.mouse)
        # Let's start the show
        print "executing paint"
        self.execute([self.paint], 10.0)
        print "executing mouse, keyboard, paint"
        self.execute([self.mouse, self.keyboard, self.paint], 10.0)
        pygame.quit()


    def tick(self):
        # Poll pygames event queue and dispatch our events
        for event in pygame.event.get():
            self.dispatch_event(event.type)


    #########################################################################
    # Our event handlers
    #########################################################################
    def paint(self):
        print "print"

    def mouse(self):
        print "mouse"

    def keyboard(self):
        print "keyboard"

