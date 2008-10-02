#!/usr/bin/env python

# As we all know - there are "lies, damned lies, and benchmarks".

# benchmark.py -
# Copyright (C) 2008  Bastian Venthur
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


import bcinetwork

import time
import socket

CONTROL_SIGNAL = """
<bci-signal>
<control-signal version="1.0">
    <tuple name="tuple">
        <i name="id" value="%(id)i" />
        <f name="time" value="%(time)f" />
    </tuple>
</control-signal>
</bci-signal>
"""

def test_clock_precision():
    """Test the minimum, non zero time difference measurable in python."""
# TODO: under Windows it's possibly more precise to use time.clock()
# if sys.platform == 'win32':
#     _timer = time.clock
# else:
#     _timer = time.time
    
    deltas = []
    for i in range(100000):
        t1 = time.time()
        t2 = time.time()
        # Just in case t1 == t2, measure again until both values are different
        while t1 == t2:
            t2 = time.time()
        deltas.append(t2-t1)
    return deltas


def min_max_avg(tseries, factor=None):
    """Take a time series and calculate the min, max and average value."""
    
    minv, maxv, avgv = min(tseries), max(tseries), sum(tseries)/len(tseries)
    if factor:
        minv *= factor
        maxv *= factor
        avgv *= factor
    return minv, maxv, avgv


def pretty_print(tseries, description, factor=None):
    """Pretty print min, max and avg of a given time series."""
    
    min, max, avg = min_max_avg(tseries, factor)
    time = "seconds"
    if factor == 1000:
        time = "milli"+time
    elif factor == 1000000:
        time = "micro"+time
    s = """%(description)s: 
    Min: %(min)f %(time)s
    Max: %(max)f %(time)s
    Avg: %(avg)f %(time)s""" % {"description" : description, "min" : min, "max" : max, "avg" : avg, "time" : time}
    print s


def test_latency(packets, delay=None):
    """Measure the latency between the BCI system and the on_cs_event in the Feedback."""
    _load_feedback()
    time.sleep(1)
    _send_cs(packets, delay)
    time.sleep(1)
    d = _get_data()
    deltas = []
    for id, t1, t2 in d:
        deltas.append(t2-t1)
    return deltas


def _load_feedback():
    bcinet = bcinetwork.BciNetwork(bcinetwork.LOCALHOST, bcinetwork.FC_PORT)
    bcinet.send_init("BenchmarkFeedback")

def _get_data():
    bcinet = bcinetwork.BciNetwork(bcinetwork.LOCALHOST, bcinetwork.FC_PORT, bcinetwork.GUI_PORT)
    v = bcinet.get_variables()
    if not v:
        return []
    else: 
        return v["data"]

def _send_cs(packets, delay, id=0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (bcinetwork.LOCALHOST, bcinetwork.FC_PORT)
    if delay:
        for i in range(packets):
            time.sleep(delay)
            id += 1
            t = time.time()
            s = CONTROL_SIGNAL % {"id" : id, "time" : t}
            sock.sendto(s, address)
    else:
        # burst mode
        for i in range(packets):
            id += 1
            t = time.time()
            s = CONTROL_SIGNAL % {"id" : id, "time" : t}
            sock.sendto(s, address)
    

if __name__ == "__main__":
    
    d = test_clock_precision()
    pretty_print(d, "Clock resolution", 1000000)

    samples_hz = (10, 1), (100, 10), (100, 100), (100, 1000), (100, None)
    for samples, hz in samples_hz:
        delay = 1.0/hz if hz else None
        d = test_latency(samples, delay)
        hz = "%iHz" % hz if hz else "burst mode"
        pretty_print(d, "BCI->Feedback Latency with %i samples in %s" % (samples, hz), 1000)
    