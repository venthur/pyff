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
    start_bv_recorder(self)
    
def post_play(self): pass

def pre_pause(self):  pass
def post_pause(self): pass

def pre_stop(self):
    stop_bv_recorder(self)
    
def post_stop(self): pass
################################################################################
# /Feedback Controller Hooks
################################################################################

try:
    import external.RecorderRemoteControl.RecorderRemoteControl as rcc
except ImportError, e:
    print "Unable to import", str(e)

import os

def start_bv_recorder(self):
    # save to filename TODAY_DIR BASENAME VP_CODE
    todayDir = self.fc_data.get("TODAY_DIR")
    basename = self.fc_data.get("BASENAME")
    vbCode = self.fc_data.get("VP_CODE")
    if not (todayDir and basename and vbCode):
        # one or more of the variables is missing
        todayDir = ("UNKNOWN_DATE")
        basename = ("UNKNOWN_BASE")
        vbCode = ("UNKNOWN_VP")
    filename = os.sep.join([str(todayDir), str(basename), str(vbCode)])
    print "Recoding to file: ", filename
    rcc.startRecording(filename)


def stop_bv_recorder(self):
    rcc.stopRecording()