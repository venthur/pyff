#!/usr/bin/env python

# FeedbackController.py -
# Copyright (C) 2007-2014  Bastian Venthur
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


"""Main Module for Feedback Controller executable."""


import logging
import logging.handlers
from optparse import OptionParser
from multiprocessing import Process

import GUI
from lib.feedbackcontroller import FeedbackController


def main():
    """Start the Feedback Controller."""

    # Get Options
    description = """Feedback Controller"""
    usage = "%prog [Options]"
    version = """
Copyright (C) 2007-2014 Bastian Venthur <bastian.venthur at tu-berlin de>

Homepage: http://bbci.de/pyff

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
    parser = OptionParser(usage=usage, version=version, description=description)
    parser.add_option('-l', '--loglevel', type='choice',
                      choices=['critical', 'error', 'warning', 'info', 'debug', 'notset'],
                      dest='loglevel',
                      help='Which loglevel to use for everything but the Feedbacks. Valid loglevels are: critical, error, warning, info, debug and notset. [default: warning]',
                      metavar='LEVEL')
    parser.add_option('--fb-loglevel', type='choice',
                      choices=['critical', 'error', 'warning', 'info', 'debug', 'notset'],
                      dest='fbloglevel',
                      help='Which loglevel to use for the Feedbacks. Valid loglevels are: critical, error, warning, info, debug and notset. [default: warning]',
                      metavar='LEVEL')
    parser.add_option('--logserver', dest='logserver',
                      action='store_true', default=False,
                      help='Send log output to logserver.')
    parser.add_option('-a', '--additional-feedback-path', dest='fbpath',
                      action='append',
                      help="Additional path to search for Feedbacks. Use this option several times if you want to add more than one path.",
                      metavar="DIR")
    parser.add_option('--port', dest='port',
                      help="Set the Parallel port address to use. Windows only. Should be in Hex (eg: 0x378)",
                      metavar="PORTNUM")
    parser.add_option("--nogui", action="store_true", default=False,
                      help="Start without GUI.")
    parser.add_option("--protocol", dest='protocol', type='choice',
                      help="Set the protocol to which Pyff listens to. Options are: json, bcixml and tobixml.",
                        choices=['bcixml', 'json', 'tobixml'], default='bcixml')

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

    if options.logserver:
        rootLogger = logging.getLogger('')
        socketHandler = logging.handlers.SocketHandler('localhost',
                                                       logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        rootLogger.addHandler(socketHandler)
        formatter = logging.Formatter('[%(process)-5d:%(threadName)-10s] %(name)-25s: %(levelname)-8s %(message)s')
        socketHandler.setFormatter(formatter)
    else:
        logging.basicConfig(level=loglevel, format='[%(process)-5d:%(threadName)-10s] %(name)-25s: %(levelname)-8s %(message)s')
    logging.info('Logger initialized with level %s.' % options.loglevel)
    logging.getLogger("FB").setLevel(fbloglevel)

    # get the rest
    fbpath = options.fbpath
    guiproc = None
    if not options.nogui:
        guiproc = Process(target=GUI.main, args=(options.protocol,))
        guiproc.start()

    port = None
    if options.port != None:
        port = int(options.port, 16)
    try:
        fc = FeedbackController(fbpath, port, options.protocol)
    except:
        logging.exception("Could not start Feedback Controller, is another instance already running?")
        return
    try:
        fc.start()
    except (KeyboardInterrupt, SystemExit):
        logging.debug("Caught keyboard interrupt or system exit; quitting")
    except:
        logging.exception("Caught an exception, quitting FeedbackController.")
    finally:
        print
        print "Stopping FeedbackController...",
        fc.stop()
        print "Done."
        if guiproc:
            print "Stopping GUI...",
            guiproc.terminate()
            print "Done."
        print "Stopping logging facilities...",
        logging.shutdown()
        print "Done."


if __name__ == '__main__':
    main()

