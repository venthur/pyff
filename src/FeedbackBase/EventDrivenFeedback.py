# EventDrivenFeedback.py -
# Copyright (C) 2009  Bastian Venthur
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


import time

from Feedback import Feedback


class EventDrivenFeedback(Feedback):

    def on_init(self):
        self.event_method_mapping = dict()
        self.enabled_methods = list()


    def on_play(self):
        self.run()


    def run(self):
        # Your script goes here.
        # You should populate this method with execute calls.
        pass


    def tick(self):
        # Your code to get events and dispatch events goes here.
        # You should poll the event queue of your toolkit/library/etc and
        # translate their events to yours.
        pass


    def execute(self, methodlist, runtime):
        """Enable given methods for a certain time."""
        self.enabled_methods = methodlist
        elapsed_time = 0.0
        t_start = time.time()
        while elapsed_time < runtime:
            self.tick()
            elapsed_time = time.time() - t_start


    def dispatch_event(self, event):
        """Dispatch the event and run the associated method if enabled."""
        method = self.event_method_mapping.get(event)
        if method and method in self.enabled_methods:
            # Call the event method
            method()


    def bind_event_to_method(self, event, method):
        """Bind event to methodcall."""
        self.event_method_mapping[event] = method

