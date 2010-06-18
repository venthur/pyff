# OrthogonalDesign.py -
# Copyright (C) 2010 Matthias Treder
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

"""
Given some factors and the total number of trials, orthogonal design builds
a list of length nTrials wherein all factor combinations appear with the same
frequency.

Example:
OrthogonalDesign([(1,2),(3,4)],nTrials=8)
specifies a 2x2 design. The output is [(1,3),(1,4),(2,3),(2,4),(1,3),(1,4),(2,3),(2,4)].
"""


def orthogonalDesign(factors,nTrials,buildup=[],trials=[]):

    # recursion exit strategy
    if factors==[]:
        trials.append(buildup)
        return
    # Start recursion
    if nTrials is not None:
        trials = []
        nSubconditions = 1
        for ii in range(len(factors)):
            nSubconditions *= len(factors[ii])
        for ii in range(nTrials/nSubconditions):
            orthogonalDesign(factors,None,[],trials)
        return trials
    else:
        ff = factors[0]
        for ii in range(len(ff)):
            orthogonalDesign(factors[1:],None,buildup+[ff[ii]],trials)

