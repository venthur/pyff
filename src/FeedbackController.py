#!/usr/bin/env python

# FeedbackController.py -
# Copyright (C) 2007-2009  Bastian Venthur
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


import logging
from optparse import OptionParser
from multiprocessing import Process

import GUI
from lib.feedbackcontroller import FeedbackController


def main():
    
    # Get Options
    description = """Feedback Controller"""
    usage = "%prog [Options]"
    version = """
Copyright (C) 2007-2009 Bastian Venthur <venthur at cs tu-berlin de>

Homepage: http://bbci.de/pyff

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
    parser = OptionParser(usage=usage, version=version, description=description)
    parser.add_option('-l', '--loglevel', type='choice', choices=['critical',
        'error',                                                  'warning', 'info', 'debug', 'notset'], dest='loglevel',
        help='Which loglevel to use for everything but the Feedbacks. Valid loglevels are: critical, error, warning, info, debug and notset. [default: warning]',
        metavar='LEVEL')
    parser.add_option('--fb-loglevel', type='choice', choices=['critical',
        'error', 'warning', 'info', 'debug', 'notset'], dest='fbloglevel',
        help='Which loglevel to use for the Feedbacks. Valid loglevels are: critical, error, warning, info, debug and notset. [default: warning]',
        metavar='LEVEL')
    parser.add_option('-p', '--plugin', dest='plugin',
                      help="Optional Plugin, the Feedback Controller should load.",
                      metavar="MODULE")
    parser.add_option('-a', '--additional-feedback-path', dest='fbpath',
                      help="Additional path to search for Feedbacks.",
                      metavar="DIR")
    parser.add_option('--port', dest='port',
                      help="Set the Parallel port address to use. Windows only. Should be in Hex (eg: 0x378)",
                      metavar="PORTNUM")
    parser.add_option("--nogui", action="store_true", default=False, 
                      help="Start without GUI.")


    options, args = parser.parse_args()

    # Initialize logging
    str2loglevel = {'critical' : logging.CRITICAL,
                    'error'    : logging.ERROR,
                    'warning'  : logging.WARNING,
                    'info'     : logging.INFO,
                    'debug'    : logging.DEBUG,
                    'notset'   : logging.NOTSET}
    
    loglevel = str2loglevel.get(options.loglevel, logging.WARNING)
    fbloglevel = str2loglevel.get(options.fbloglevel, logging.WARNING)

    logging.basicConfig(level=loglevel, format='[%(process)-5d:%(threadName)-10s] %(name)-25s: %(levelname)-8s %(message)s')
    logging.info('Logger initialized with level %s.' % options.loglevel)
    logging.getLogger("FB").setLevel(fbloglevel)
    
    # get the rest
    plugin = options.plugin
    fbpath = options.fbpath
    if not options.nogui:
        guiproc = Process(target=GUI.main)
        guiproc.start() 
        
    port = None
    if options.port != None:
        port = int(options.port, 16)
    try:
        fc = FeedbackController(plugin, fbpath, port)
        fc.start()
    except (KeyboardInterrupt, SystemExit):
        fc.stop()
        logging.debug("Caught keyboard interrupt or system exit; quitting")


if __name__ == '__main__':
    main()
