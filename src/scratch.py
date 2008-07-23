# scratch.py -
# Copyright (C) 2007-2008  Bastian Venthur
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

import os
import Feedback
import traceback

def test_feedback(root, file):
    # remove trailing .py if present
    if file.lower().endswith(".py"):
        file2 = file[:-3]
    root = root.replace("/", ".")
    while root.startswith("."):
        root = root[1:]
    if not root.endswith(".") and not file2.startswith("."):
        module = root + "." + file2
    else:
        module = root + file2
    valid, name = False, file2
    mod = None
    try:
        mod = __import__(module, fromlist=[None])
        #print "1/3: loaded module (%s)." % str(module)
        fb = getattr(mod, file2)(None)
        #print "2/3: loaded feedback (%s)." % str(file2)
        if isinstance(fb, Feedback.Feedback):
            #print "3/3: feedback is valid Feedback()"
            valid = True
    except:
        print "Ooops! Something went wrong loading the feedback"
        print traceback.format_exc()
    finally:
        del mod
        return valid, name
    
    

def get_feedbacks():
    """Returns the valid feedbacks in this directory."""
    feedbacks = {}
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.lower().endswith(".py"):
                # ok we found a candidate, check if it's a valid feedback
                isFeedback, name = test_feedback(root, file)
                if isFeedback:
                    feedbacks[name] = root+file
    for i in feedbacks.items():
        print i

    

if __name__ == "__main__":
    fb = get_feedbacks()
    print dir()

