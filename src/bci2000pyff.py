# bci2000pyff.py -
# Copyright (C) 2012  Bastian Venthur
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


"""BCI2000 to Pyff adapter.

This module provides methods and classes needed by BCI2000 to run Pyff
Feedback- and Stimulus applications.

"""

import logging
import copy
import multiprocessing
import threading
import time


LOGLEVEL = logging.NOTSET

# Setup the logging
logging.basicConfig(format='%(asctime)s %(name)-10s %(levelname)8s %(message)s', level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.info('Logger started')


class Bci2000PyffAdapter(object):
    """BCI2000 to Pyff Feedback adapter.

    This class bridges BCI2000 and Pyff Feedback/Stimulus applications
    (Feedbacks). It provides an interface BCI2000 needs to talk to Feedbacks.
    Do not subclass this class, this class will create instances of Pyff
    Feedbacks and delegate the calls to them.

    """

    def __init__(self):
        self._error_reported = False
        self._writeable_params = []
        self._errors = ""

    def _Construct(self):
        logger.debug('_Construct')
        # Fixme this is just an example and should be set by the BCI2000
        self.fbmod = 'Feedbacks.TrivialPong.TrivialPong'
        self.fbclassname = 'TrivialPong'
        # OnInit
        import sys
        import os
        # needed because we run processes from within an embedded python
        # interpreter
        multiprocessing.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))
        sys.argv = [""]
        self.mycon, childcon = multiprocessing.Pipe()
        self.feedback_proc = multiprocessing.Process(target=feedback_process_loop, args=(self.fbmod, self.fbclassname, childcon,))
        self.feedback_proc.start()
        # returns variables of the feedback in form of parameter lines
        return [], []

    def _Halt(self):
        logger.debug('_Halt')
        pass

    def _Preflight(self, in_signal_props):
        logger.debug('_Preflight')
        try:
            pass
        except Exception, e:
            self._handle_error(str(e))
        return copy.deepcopy(in_signal_props)

    def _Initialize(self, in_signal_dim, out_signal_dim):
        logger.debug('_Initialize')
        # set variables from parameters
        pass

    def _StartRun(self):
        logger.debug('_StartRun')
        self.mycon.send('play')

    def _Process(self, in_signal):
        logger.debug('_Process')
        try:
            pass
            # OnControlEvent
        except Exception, e:
            self._handle_error(str(e))
        return copy.deepcopy(in_signal)

    def _StopRun(self):
        logger.debug('_StopRun')
        self.mycon.send('stop')

    def _Resting(self):
        logger.debug('_Resting')
        pass

    def _Destruct(self):
        logger.debug('_Destruct')
        self.mycon.send('quit')
        self.mycon.close()
        self.feedback_proc.join()

    def _call_hook(self, method, *pargs, **kwargs):
        logger.debug('_call_hook(%s, %s, %s)' % (method, pargs, kwargs))
        try:
            retval = method(*pargs, **kwargs)
        except Exception, e:
            retval = None
            self._handle_error(str(e))
        return retval

    def _set_state_precisions(self, bits):
        pass

    def _set_states(self, states):
        self._states = states

    def _get_states(self):
        return self._states

    def _set_parameters(self, params):
        self._parameters = params

    def _get_parameters(self):
        return {}

    def _param_labels(self, param_name, row_labels, column_labels):
        pass

    def _handle_error(self, error):
        self._errors = self._errors + "\n" + error
        self._error_reported = True

    def _flush_error_info(self):
        errors = self._errors
        self._errors = ""
        self._error_reported = False
        return errors, True


def feedback_process_loop(fbmodule, classname, con):
    mod = __import__(fbmodule, fromlist=[classname])
    fbclass = getattr(mod, classname)
    fb = fbclass()
    fb_ipc_thread = threading.Thread(target=feedback_ipc_loop, args=(fb, con))
    fb_ipc_thread.start()
    try:
        fb.on_init()
        fb._playloop()
    finally:
        con.close()
        fb_ipc_thread.join()


def feedback_ipc_loop(fb, con):
    while 1:
        data = con.recv()
        logger.debug('Received %s message' % data)
        if data == 'quit':
            fb._on_quit()
            break
        if data == 'play':
            fb._playEvent.set()
        elif data == 'pause':
            fb._on_pause()
        elif data == 'stop':
            fb._on_stop()


if __name__ == '__main__':
    adapter = Bci2000PyffAdapter()
    adapter.fbmod = 'Feedbacks.TrivialPong.TrivialPong'
    adapter.fbclassname = 'TrivialPong'
    adapter._Construct()
    adapter._StartRun()
    time.sleep(2)
    adapter._StopRun()
    time.sleep(2)
    adapter._Destruct()

