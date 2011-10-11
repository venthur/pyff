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

from random import Random, choice, randint
from copy import copy
from itertools import chain
import logging

from RSVPSpeller.util.list import slices, remove_all
from RSVPSpeller.sequence_algorithm import RSVP

class CharacterSequence(list):
    def __init__(self, sequence, redundance, burst_count=3, alt_color=False,
                 palette=None):
        list.__init__(self, [])
        self.sequence = list(sequence)
        self._redundance = redundance
        self._burst_count = burst_count
        self._alt_color = alt_color
        self._palette = palette
        self.__init_attributes()

    def __init_attributes(self):
        self._random = Random('BBCI')
        self._burst_signi_len = len(self.sequence) / self._burst_count
        self._redundance_len = len(self._redundance)
        self._burst_len = self._burst_signi_len + self._redundance_len
        self._sequence = copy(self.sequence)
        self._create_burst_sequence()
        self._zip_colors()

    def _create_burst_sequence(self):
        """ Insert redundant symbols into the character sequence. """
        make_burst = lambda b: self._new_redundance + b
        bursts = map(make_burst, slices(self._sequence, self._burst_signi_len))
        self.burst_sequence = list(chain(*bursts))

    def _zip_colors(self):
        """ Create a list of alternating colors and zip them to the
        burst sequence, keep as a list of burst lists.
        """
        nsym = len(self.burst_sequence)
        self._colors = map(self._positional_color, xrange(nsym))
        zipped = zip(self.burst_sequence, self._colors)
        self[:] = zipped
        self.bursts = slices(zipped, self._burst_len)

    def _positional_color(self, i):
        if self._alt_color:
            return self._palette(i)

    @property
    def _new_redundance(self):
        return self._random.sample(self._redundance, self._redundance_len)

class CharacterSequenceFactory(object):
    def __init__(self, redundance, alt_color, target, palette):
        self._redundance = redundance
        self._alt_color = alt_color
        self._target = target
        self._palette = palette
        try:
            self._color_offset = (i for i, g in enumerate(self._palette.groups)
                                  if self._target in g).next()
        except StopIteration, e:
            self._color_offset = -1
        self._rsvp = RSVP(self._palette.groups)

    def sequence(self, sequence):
        return CharacterSequence(sequence, self._redundance,
                                 alt_color=self._alt_color,
                                 palette=self._palette)

    def extra_sequence(self, target_count_interval):
        """ Create one sequence with additional targets at random
        positions, preserving the color groups. If color mode is
        off, don't preserve. Restrict to 10 targets.
        """
        start, stop = target_count_interval
        target_count = choice(range(start, stop + 1))
        target_count = min(target_count, 10)
        bursts = self._rsvp.trial(2, self._alt_color) 
        seq = sum(bursts[:3], [])
        if self._alt_color:
            indexes = range(0, len(seq), 3)
            random_index = lambda: self._color_offset + choice(indexes)
            while len(filter(lambda l: l == self._target, seq)) < target_count:
                seq[random_index()] = self._target
        else:
            indexes = range(0, len(seq))
            random_index = lambda: choice(indexes)
            while indexes and len(filter(lambda l: l == self._target,
                                         seq)) < target_count:
                index = random_index()
                seq[index] = self._target
                remove_all(indexes, range(index - 1, index + 2))
        return self.sequence(seq)

    def sequences(self, count, pre=[], post=[]):
        main_bursts = self._rsvp.trial(count, self._alt_color) 
        main_seqs = [sum(main_bursts[i:i + 3], []) for i in
                     xrange(0, len(main_bursts), 3)]
        extra = self.extra_sequence
        sequences = map(extra, pre) + map(self.sequence, main_seqs) + map(extra,
                                                                         post)
        return Sequences(sequences)

class Sequences(list):
    def occurences(self, symbol):
        return sum(len(filter(lambda s: s == symbol, seq.burst_sequence)) for
                   seq in self)
