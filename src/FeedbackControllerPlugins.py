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
    self.logger.debug('Running pre_play.')
    start_bv_recorder(self)
    
def post_play(self): pass

def pre_pause(self):  pass
def post_pause(self): pass

def pre_stop(self):
    stop_bv_recorder(self)
    
def post_stop(self): pass

def pre_quit(self):  pass
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
    todayDir = self.fc_data.get("TODAY_DIR")
    basename = self.fc_data.get("BASENAME")
    vbCode = self.fc_data.get("VP_CODE")
    if not (todayDir and basename and vbCode):
        self.logger.error("todayDir, basename or vbCode variable does not exist in the Feedback Controller")
        return
    # test if todayDir acutally exists
    if not os.path.exists(todayDir):
        self.logger.error("Directory does not exist, cannot record to: %s" % str(todayDir))
        return
    
    filename = os.sep.join([str(todayDir), str(basename) + str(vbCode)])
    self.logger.debug("Recoding to file: %s" % filename)
    try:
        rcc.startRecording(filename)
    except Exception, e:
        self.logger.error("Unable to start recording:")
        self.logger.error(str(e))
        self.logger.error(str(traceback.format_exc()))


def stop_bv_recorder(self):
    try:
        rcc.stopRecording()
    except:
        self.logger.error("Unable to stop recording:")
        self.logger.error(str(e))