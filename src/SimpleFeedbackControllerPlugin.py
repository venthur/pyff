# FeedbackControllerPlugins.py -
# Copyright (C) 2008-2009  Bastian Venthur
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



#
# BBCI specific Feedback Controller Plugins
# it is SAFE to remove this file if you don't need those plugins.
#
# You can modify those methods as needed.


################################################################################
# Feedback Controller Hooks
################################################################################
def pre_init(self):
    self.logger.debug("Pre Init.")
    
def post_init(self): pass

def pre_play(self):
    self.logger.debug("Pre Play.")

    
def post_play(self): pass

def pre_pause(self):
    self.logger.debug("Pre Pause.")
    
def post_pause(self): pass

def pre_stop(self):
    self.logger.debug("Pre Stop.")
    
def post_stop(self): pass

def pre_quit(self):
    self.logger.debug("Pre Quit.")

def post_quit(self): pass
################################################################################
# /Feedback Controller Hooks
################################################################################
