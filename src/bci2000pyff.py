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

import numpy


LOGLEVEL = logging.NOTSET

# Setup the logging
logging.basicConfig(format='%(asctime)s %(name)-10s %(levelname)8s %(message)s', level=LOGLEVEL)
logger = logging.getLogger(__name__)
logger.info('Logger started')


def register_framework_dir():
    logger.debug('Register Framework')
    pass


def register_working_dir():
    logger.debug('Register Working Dir')
    pass


def search_for_file(filename):
    logger.debug('Search For File')
    pass


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
        # OnInit
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
        # OnPlay
        pass

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
        # OnStop
        pass

    def _Resting(self):
        logger.debug('_Resting')
        pass

    def _Destruct(self):
        logger.debug('_Destruct')
        # OnQuit
        pass

    def _call_hook(self, method, *pargs, **kwargs):
        logger.debug('_call_hook(%s, %s, %s)' % (method, pargs, kwargs))
        try:
            retval = method(*pargs, **kwargs)
        except Exception, e:
            retval = None
            self._handle_error(str(e))
        return retval

    def _sharing_setup(self, indims, outdims, statelist):
        logger.debug('_sharing_setup')
        return ()

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

    def _enable_shell(self):
        pass

    def _start(self):
        pass

    def _zeros(self, nrows, ncols):
        return numpy.asmatrix(numpy.zeros((nrows, ncols), dtype=numpy.float64, order='C'))
