#!/usr/bin/env python

# testsuite.py
# Copyright (C) 2007-2011  Bastian Venthur
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

import unittest
import logging
import os

# Setup the loggger
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
                    )
logging.disable(100)

# Walk through every subdir and search for folders named "test".
# For every python file in those folders should contain TestCases by convention.
allTests = unittest.TestSuite()

for root, dirs, files in os.walk("."):
    if root.split(os.sep)[-1] == "test":
        for file in files:
            if file.endswith(".py"):
                module = root.replace(os.sep, ".")+"."+file[:-3]
                while module.startswith("."):
                    module = module[1:]
                try:
                    suite = unittest.TestLoader().loadTestsFromName(module)
                    allTests.addTest(suite)
                except Exception, e:
                    logging.warning("Unable to add %s" % module)
                    logging.warning(e)

# Run the tests
unittest.TextTestRunner(verbosity=2).run(allTests)
