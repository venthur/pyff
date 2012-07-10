# eyetracker.py -
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

# History
# 27/02/2009 - Chris Hausler - adapted to use CEtApi directly
#
#

import threading
import logging
import sys, os
import ctypes
import time
from ctypes import *
from struct import *
import datetime



class AleaData(ctypes.Structure):
    """Class to contain data returned from API event."""
    _fields_ = [("rawDataTimestamp", ctypes.c_long),
                ("intelligazeX", ctypes.c_double),
                ("intelligazeY", ctypes.c_double),
                ("gazePositionXLeftEye", ctypes.c_double),
                ("gazePositionYLeftEye", ctypes.c_double),
                ("gazePositionConfidenceLeftEye", ctypes.c_double),
                ("pupilDiameterLeftEye", ctypes.c_double),
                ("gazePositionXRightEye", ctypes.c_double),
                ("gazePositionYRightEye", ctypes.c_double),
                ("gazePositionConfidenceRightEye", ctypes.c_double),
                ("pupilDiameterRightEye", ctypes.c_double),
                ("eventID", ctypes.c_int),
                ("eventDataTimestamp", ctypes.c_long),
                ("duration", ctypes.c_long),
                ("positionX", ctypes.c_double),
                ("positionY", ctypes.c_double),
                ("dispersionX", ctypes.c_double),
                ("dispersionY", ctypes.c_double),
                ("confidence", ctypes.c_double)]


# event types
eventArray = 'Fixation detected', 'Saccade detected', 'Blink detected', 'No Event detected'
# calibration statuses
calibrationStatus = 'Excellent' , 'Good' , 'Average' , 'Poor' , 'Failed'


class EyeTracker(object):
    """EyeTracker.

    Example::

        import time
        et = EyeTracker()
        et.start()
        time.sleep(60)
        # read something
        et.stop()

    """

    def __init__(self):
        self.logger = logging.getLogger("EyeTracker")
        self.logger.debug("Logger initialized.")
        self.thread = None
        self.stopping = True
        self.time_h = None
        self.time_m = None
        self.time_s = None
        self.time_ms = None
        self.x = None
        self.y = None
        self.duration = None


    def initialise_api(self):
        # Load dll
        path = os.path.dirname(globals()["__file__"])
        self.api = WinDLL(os.path.join(path, 'CEtAPI'))
        #Open API
        result = self.api.Open()
        if(result == 0):
            self.logger.debug("API open")
        else:
            self.logger.debug("Could not open API")
            return False
        #API open?
        isOpen = c_short()
        result = self.api.IsOpen(byref(isOpen))
        if(result == 0):
            self.logger.debug("IsOpen call succeed")
            if(isOpen):
                self.logger.debug("API is open")
            else:
                self.logger.debug("API is not open")
                return False
        else:
            self.logger.debug("IsOpen call failed")
            return False
        #Get Version of API
        major = c_long()
        minor = c_long()
        build = c_long()
        device = c_long()
        result = self.api.Version(byref(major), byref(minor), byref(build), byref(device))
        if(result == 0):
            self.logger.debug("Version call succeed")
            self.logger.debug('Version: ' + str(major.value) + '.' + str(minor.value) + '.' + str(build.value))
            self.logger.debug('Device: ' + str(device.value))
        else:
            self.logger.debug("Version call failed")
        return True


    def start(self):
        """Start the Eyetracker."""
        self.logger.debug('Starting Eye Tracker')
        self.thread = threading.Thread(target=self.listen)
        self.stopping = False
        self.thread.start()


    def stop(self):
        """Stop the Eyetracker."""
        self.logger.debug('Stopping Eye Tracker')
        self.stopping = True
        self.thread.join(1)
        self.thread = None


    def listen(self):
        try:
            ## initailise the api
            if not self.initialise_api():
                self.logger.debug("Can't initialise api")
                return
            #Start DataStreaming
            result = self.api.DataStreaming(True)
            if(result == 0):
                self.logger.debug("DataStreaming call succeed")
            else:
                self.logger.debug("DataStreaming call failed")
                return
            # clear buffer
            if(self.api.ClearDataBuffer() == 0):
                self.logger.debug("ClearBuffer call succeed")
            else:
                self.logger.debug("ClearBuffer call failed")
            data = AleaData()
            # while not stopped, handle events
            while not self.stopping:
                result = self.api.WaitForData(byref(data), 1000)
                if(result == 0):
                    # fixation event
                    if data.eventID == 0:
                        # TODO: check date format and handle here
                        now = datetime.datetime.now()
                        self.time_h = now.hour
                        self.time_m = now.minute
                        self.time_s = now.second
                        self.time_ms = now.microsecond / 1000
                        self.x = int(data.positionX)
                        self.y = int(data.positionY)
                        self.duration = int(data.duration)
                        # can be used for debug
                        #print 'x', self.x
                        #print 'y', self.y
                        #print 'duration', self.duration
                        #print 'h', self.time_h
                        #print 'm', self.time_m
                        #print 's', self.time_s
                        #print 'ms', self.time_ms
            #Stop DataStreaming
            result = self.api.DataStreaming(False)
            self.logger.debug("Close Api now")
            result = self.api.Close()
            self.logger.debug("Api closed")
            windll.kernel32.FreeLibrary(self.api._handle)
        except:
            self.logger.debug("Listen Failed!")
            # This is not useful, a thread cannot join itself
            # 2009-07-15 Basti
            #self.stop()


    def calibrate(self):
        """Call calibration for the eye tracker."""

        print("Perform calibration. Press Enter to start calibration")
        sys.stdin.readline()
        result = api.PerformCalibration(5, 0, False, False, True, 0, True, True, True, hex2dec('C0C0C0'), hex2dec('0000FF') , "")
        if(result == 0):
            self.logger.debug("PerformCalibration call succeed")
            status = c_int()
            improve = c_short()
            #Wait for CalibrationDone without Timeout
            result = api.WaitForCalibrationResult(byref(status), byref(improve), -1)
            if(result == 0):
                str_result = 'Calibration Result: ' + calibrationStatus[status.value]
                str_improve = 'Improve: ' + str(improve.value)
                print str_result
                print str_improve
                self.logger.debug(str_result)
                self.logger.debug(str_improve)
            else:
                self.logger.debug('WaitForCalibrationResult call failed')
            print("Calibration Complete")
            return True
        else:
            self.logger.debug("PerformCalibration call failed")
        return False


if __name__ == "__main__":
    import time
    et = EyeTracker()
    et.start()
    time.sleep(60)
    # read something
    et.stop()

