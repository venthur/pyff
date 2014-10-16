#!/usr/bin/env python

# emulator.py - a simple BCI system emulator
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

"""A BCI-system emulator."""


import cmd
import threading
import math
import time

from lib import bcinetwork
from lib.bcinetwork import BciNetwork
from lib import bcixml
from lib.bcixml import BciSignal


class Emulator(cmd.Cmd):

    prompt = "> "
    intro = "Welcome to the BCI emulator. Type help to see a list of available commands."

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.stopping = True

    def do_quit(self, line):
        """Quit the Emulator."""
        return True

    def postloop(self):
        print

    def do_generate_cs(self, line):
        """Generates a control signal and sends it to the Feedback Controller."""
        self._do_generate_cs(line, 1)

    def do_generate_cs2(self, line):
        """Generates a control signal and sends it to the Feedback Controller."""
        self._do_generate_cs(line, 2)

    def do_generate_cs3(self, line):
        """Generates a control signal and sends it to the Feedback Controller."""
        self._do_generate_cs(line, 3)

    def do_generate_cs4(self, line):
        """Generates a control signal and sends it to the Feedback Controller."""
        self._do_generate_cs(line, 4)

    def do_generate_cs5(self, line):
        """Generates a control signal and sends it to the Feedback Controller."""
        self._do_generate_cs(line, 5)

    def do_generate_cs6(self, line):
        """Generates a control signal and sends it to the Feedback Controller."""
        self._do_generate_cs(line, 6)


    def _do_generate_cs(self, line, numbers):
        self.net = BciNetwork("localhost", bcinetwork.FC_PORT)
        self.signal = BciSignal(None, None, bcixml.CONTROL_SIGNAL)
        self.stopping = False
        self.t = threading.Thread(target=self._cs_loop, args=(numbers,))
        self.t.start()
        print "Enter: stop_cs to stop the signal."


    def _cs_loop(self, numbers=1):
        c = 0
        while not self.stopping:
            time.sleep(0.04)
            c += 1
            r = math.radians(c)
            sample1 = math.sin(r)
            sample2 = math.sin(r/2-90.0)
            sample3 = math.sin(r/3-180.0)
            sample4 = math.sin(r-270.0)
            sample5 = math.sin(r-45.0)
            sample6 = math.sin(r-135.0)

            samples = [sample1, sample2, sample3, sample4, sample5, sample6]

            #self.signal.data = {"data" : [sample1, sample2, sample3]}
            if numbers == 1:
                self.signal.data = {"cl_output" : samples[0]}
            elif numbers <= 6:
                self.signal.data = {"cl_output" : samples[:numbers]}
            else:
                print "Error don't know how to handle %i numbers." % numbers

            self.net.send_signal(self.signal)

    def do_stop_cs(self, line):
        """Stops the loop which sends data to the Feedback Controller."""
        self.stopping = True
        self.t.join()

    def do_status(self, line):
        """Get the status of the emulator."""
        for var, val in self.__dict__.iteritems():
            print str(var), str(val)



if __name__ == "__main__":
    Emulator().cmdloop()
