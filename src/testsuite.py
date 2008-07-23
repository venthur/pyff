#!/usr/bin/env python

# testsuite.py
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

import tests.testUdpDecoder

import unittest
import logging

# Setup the loggger
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
                    )

# Setup the tests
allTests = unittest.TestSuite()
allTests.addTest(tests.testUdpDecoder.suite)

# Run the tests
unittest.TextTestRunner(verbosity=2).run(allTests)
