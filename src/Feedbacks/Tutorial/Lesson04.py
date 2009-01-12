# Lesson04 - Reacting on control- and interaction events
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


from FeedbackBase.Feedback import Feedback

class Lesson04(Feedback):
    
    def on_init(self):
        self.myVariable = None
        self.eegTuple = None
    
    def on_interaction_event(self, data):
        # this one is equivalent to:
        # self.myVariable = self._someVariable
        self.myVariable = data.get("someVariable")
        print self.myVariable
        
    def on_control_event(self, data):
        # this one is equivalent to:
        # self.eegTuple = self._data
        self.eegTuple = data
        print self.eegTuple
