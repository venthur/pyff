#!/usr/bin/env python

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
