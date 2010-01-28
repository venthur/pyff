""" {{{ Copyright (c) 2009 Torsten Schmits

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this
program; if not, see <http://www.gnu.org/licenses/>.

}}} """

from random import Random
from copy import copy

class LetterSequence(object):
    def __init__(self, alphabet, burst_count=3):
        self._alphabet = list(alphabet)
        self._burst_count = burst_count
        self.__init_attributes()
        self.reset()

    def __init_attributes(self):
        self._random = Random('BBCI')
        self._burst_len = len(self._alphabet) / self._burst_count
        self.done = False

    def reset(self):
        self._sequence = copy(self._alphabet)
        self._random.shuffle(self._sequence)
        self._bursts = map(self._create_burst, xrange(self._burst_count))
        self._current_index = 0
        self.done = False

    def _create_burst(self, i):
        l = self._burst_len
        return self._random.sample(self._alphabet, 6) + \
               self._sequence[i * l:(i + 1) * l]

    @property
    def next_burst(self):
        burst = self._bursts[self._current_index]
        self.done = self._current_index + 1 == len(self._bursts)
        if not self.done:
            self._current_index += 1
        return burst
