#!/usr/bin/env python

# trigger.py - Common trigger definitions.
# Copyright (C) 2010  Bastian Venthur <bastian.venthur@tu-berlin.de>
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


"""Common trigger definitions.

This file contains common trigger definitions. You should use those here
instead of defining them in your Feedback or Stimulus applications whenever
possible.

This module is executable. When called as a script it will check for duplicate
trigger definitions and will warn you about it. You should call this module
whenever you modified or added new trigger definitions.
"""


# Markers specifying the start and the end of the run. They should be sent
# when the feedback is started resp. stopped.
RUN_START, RUN_END = 254, 255

# Start resp. end of a trial
TRIAL_START, TRIAL_END = 250, 251

# Start resp. end of a countdown
COUNTDOWN_START, COUNTDOWN_END = 240, 241

# Onset resp. offset of a fixation marker
FIXATION_START,FIXATION_END = 242, 243

# Onset resp. offset of a cue
CUE_START, CUE_END = 244, 245

# Onset resp. offset of feedback
FEEDBACK_START, FEEDBACK_END = 246, 247

# Start resp. end of a short break during the run
PAUSE_START, PAUSE_END = 248, 249


if __name__ == '__main__':
    _tmp = list()
    for name, value in globals().items():
        # ignore magic variables
        if name.startswith('__') and name.endswith('__'):
            print "Ignoring magic %s" % name
            continue
        if name == '_tmp':
            continue
        if not isinstance(value, int):
            print "Ignoring non-int %s (%s)" % (name, str(value))
        _tmp.append([value, name])
    _tmp.sort()
    for i in range(1, len(_tmp)):
        if _tmp[i][0] == _tmp[i-1][0]:
            print "Found duplicate triggers (%i) %s and %s" % (_tmp[i][0],
                    _tmp[i-1][1], _tmp[i][1])

