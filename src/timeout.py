#!/usr/bin/env python
# coding: utf8

# timeout.py -
# Copyright (C) 2007-2008  Bastian Venthur
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

# Decorator @timeout(sec), calls the method in a seperate thread with the
# specified timeout. Exceptions and the result is propagated
#
# from timeout import *
# 
# @timeout(5)
# def infinite_loop():
#    while 1:
#        pass
#
# if __name__ == "__main__":
#     try:
#         infinite_loop()
#     except ThreadMEthodTimeoutError, e:
#         # do something
#         pass
#     except Exception, e:
#         # thrown by infinite loop



from threading import Thread

class ThreadMethodTimeoutError(Exception): pass

class timeout(object):
    """Runs the method in a different thread.
    
    @timeout(timeout) is a decorator function which returns a method wrapper
    which runs the wrapped method in a different thread with a timeout.
    """
    def __init__(self, timeout):
        self.timeout = timeout
        
    def __call__(self, f):
        def _f(*args, **kwargs):
            worker = ThreadMethodThread(f, args, kwargs)
            if self.timeout is None:
                return worker
            worker.join(self.timeout)
            if worker.isAlive():
                raise ThreadMethodTimeoutError()
            elif worker.exception is not None:
                raise worker.exception
            else:
                return worker.result
        return _f


class ThreadMethodThread(Thread):
    def __init__(self, target, args, kwargs):
        Thread.__init__(self)
        self.target, self.args, self.kwargs = target, args, kwargs
        self.start()
        
    def run(self):
        try:
            self.result = self.target(*self.args, **self.kwargs)
        except Exception, e:
            self.exception = e
        except:
            self.exception = Exception()
        else:
            self.exception = None
