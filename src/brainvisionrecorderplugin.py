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
def pre_init(self):  pass
def post_init(self): pass

def pre_play(self):
    try:
        print 'Running pre_play.'
        start_bv_recorder(self)
    except:
        print "Could not start brain vision recorder."
        print str(traceback.format_exc())
    
def post_play(self): pass

def pre_pause(self):  pass
def post_pause(self): pass

def pre_stop(self):
    try:
        stop_bv_recorder(self)
    except:
        print "Could not stop brain vision recorder."
    
def post_stop(self): pass

def pre_quit(self):
    try:
        stop_bv_recorder(self)
    except:
        print "Could not stop brain vision recorder."

def post_quit(self): pass
################################################################################
# /Feedback Controller Hooks
################################################################################

try:
    import external.RecorderRemoteControl.RecorderRemoteControl as rcc
except ImportError, e:
    print "Unable to import", str(e)

import os
import traceback

def start_bv_recorder(self):
    # save to filename TODAY_DIR BASENAME VP_CODE
    # TODAY_DIR => D:\data\bbciRaw\bla\
    # BASENAME+VP_CODE = filebase
    # actual save target: TODAY_DIR\filebase
    print "Starting BV recorder..."
    todayDir = self.TODAY_DIR
    basename = self.BASENAME
    vbCode = self.VP_CODE
    if not (todayDir and basename and vbCode):
        print "todayDir, basename or vbCode variable does not exist in the Feedback Controller"
        return
    # test if todayDir acutally exists
    if not os.path.exists(todayDir):
        print "Directory does not exist, cannot record to: %s" % str(todayDir)
        return
    
    filename = os.sep.join([str(todayDir), str(basename) + str(vbCode)])
    
    suffix = ""
    num = 2
    while os.path.exists(filename+suffix+".eeg"):
        suffix = "%02i" % num
        num += 1
    filename = filename + suffix + ".eeg"
        
    print "Recoding to file: %s" % filename
    try:
        rcc.startImpRecording(filename)
    except Exception, e:
        print "Unable to start recording:"
        print str(e)
        print str(traceback.format_exc())


def stop_bv_recorder(self):
    try:
        rcc.stopRecording()
    except:
        self.logger.error("Unable to stop recording:")
        self.logger.error(str(e))

