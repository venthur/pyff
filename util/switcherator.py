""" {{{ Copyright (c) 2010 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

}}} """

class Flag(object):
    def __init__(self):
        self._flag = True

    def __nonzero__(self):
        return self._flag

    def off(self):
        self._flag = False

class Switcherator(object):
    def __init__(self, flag, itr):
        self._flag = flag
        self._iter = iter(itr)

    def __iter__(self):
        return self

    def next(self):
        if not self._flag:
            raise StopIteration()
        return self._iter.next()
