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

def slices(seq, length):
    count = len(seq) / length
    return [seq[i * length:(i + 1) * length] for i in xrange(count)]

def remove_all(seq, elements):
    for e in elements:
        try:
            seq.remove(e)
        except ValueError:
            pass

class TargetIndex(object):
    def __init__(self, word):
        self._word = word
        self._index = 0

    def __iter__(self):
        return self

    def next(self):
        old = int(self._index)
        if old >= len(self._word):
            raise StopIteration()
        self._index += 1
        return old, self._word[old]

    def delete(self):
        if self._index > 1:
            self._index -= 2
        elif self._index > 0:
            self._index -= 1
