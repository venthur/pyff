__copyright__ = """ Copyright (c) 2010 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

"""

from time import sleep

class Flag(object):
    def __init__(self):
        self.reset()

    def __nonzero__(self):
        return self._flag

    def off(self):
        self._flag = False
        self.suspended = False

    def reset(self):
        self._flag = True
        self.suspended = False

    def toggle_suspension(self):
        self.suspended = not self.suspended

    def wait(self):
        while self.suspended:
            sleep(0.1)

class Switcherator(object):
    def __init__(self, flag, itr, suspendable=False):
        self._flag = flag
        self._iter = iter(itr)
        self._suspendable = suspendable

    def __iter__(self):
        return self

    def next(self):
        if self._suspendable:
            self._flag.wait()
        if not self._flag:
            raise StopIteration()
        return self._iter.next()
