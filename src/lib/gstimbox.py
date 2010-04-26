# gstimbox.py -
# Copyright (C) 2010  Mirko Dietrich
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
g-STIMbox is a stimulator digital I/O box with an USB interface
manufactured by `g.tec medical engineering GmbH
<http://www.gtec.at/>`_. The device features 14 digital inputs and 16
digital outputs. This module encapsulates a proprietary DLL
(Dynamic-link library) that operates exclusively under `Microsoft
Windows <http://www.microsoft.com/windows/>`_.

g-STIMbox Installation
======================

In order to install the device follow these steps:

#. Get ``USB_Driver.exe`` from the g-STIMbox driver package and execute it
   with administrator privileges. It will install the driver for the USB
   serial port.
#. Connect the g-STIMbox device to a free USB socket.
#. Open the *device manager* and find *USB Serial Port* under section *Ports*.
   It should specify the virtual COM port the device is connected to in
   brackets (e.g. COM3 meaning port number 3).
#. Now you can already test the device by calling ``gSTIMboxDemo1.exe`` that
   is also included in the driver package.

For this Python module to work follow these steps:

#. Make sure the ``gSTIMbox.dll`` file is available when using the device. The
   easiest way is to put the file into the system folder (on most Windows
   installations this is ``C:\Windows\System``). Another way is to copy it to
   the same folder where this module resides.
#. Run the :mod:`demo feedback <Feedbacks.GstimboxDemo.GstimboxDemo>` or
   have a look at section :ref:`gstimbox-usage`.

For further information refer to the PDF manual shipped with the
device.

.. _gstimbox-usage:

Usage
=====

Output modes
------------

This example shows both output port operation modes (manual,
frequency).

The output ports can be either controlled manually (ON/OFF) or
assigned a specific frequency. It's possible to have different ports
operate on different modes simultaneously (e.g. port 1 and 3 work in
manual mode while 2 and 4 work in frequency mode).

Example code::

    from sys import stdout
    from time import sleep
    from gstimbox import GStimbox

    comport = 3
    b = GStimbox(comport)
    print "Connected to g-STIMbox (serial port %d)" % comport
    print "Driver version %s, firmware version %s" % \
        (b.getDriverVersion(), b.getHWVersion())
    print "Micro-controller frequency demo running..."
    stdout.flush()
    port = [0, 1, 2, 3, 4, 5, 6, 7]
    freq = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]
    mode = [1, 1, 1, 1, 1, 1, 1, 1]
    b.reset()
    b.setFrequency(port, freq)
    b.setMode(port, mode)
    sleep(10)
    b.reset()
    print "Manual ON/OFF demo running..."
    stdout.flush()
    state = [0 for i in range(16)]
    for i in range(5):
        for j in range(8):
            state[j] = 1
            b.setPortState(state)
            sleep(0.1)
        for j in range(8):
            state[j] = 0
            b.setPortState(state)
            sleep(0.1)
    b.reset()
    print "Demo finished."

.. _gstimbox-usage-input:

Processing input
----------------

In order to handle input from the g-STIMbox input ports a callback
function must be specified. The callback function receives a single
argument, a list of 14 values (e.g.  ``[0, 1, 0, 1, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0]``). Each value maps to the corresponding input port
(e.g. list index ``0`` corresponds to input port 1). In the example
input ports 2 and 4 are active while all others are not. Note that the
callback function is triggered on every state change (that is on
pressing *and* releasing of a button).

The following example prints out the complete input state vector and
activates all output ports if button on input port 1 is active
(pressed).

Example code::

    from sys import stdout
    from time import sleep
    from gstimbox import GStimbox

    def input_callback(input_vector):
        global b
        print "Input vector changed:"
        print input_vector
        b.setPortState([input_vector[0] for i in range(16)])
        stdout.flush()

    comport = 3
    b = GStimbox(comport, input_callback)
    print "Connected to g-STIMbox (serial port %d)" % comport
    print "Driver version %s, firmware version %s" % \
        (b.getDriverVersion(), b.getHWVersion())
    b.reset()
    print "Use a button connected to input port 1 to activate all output ports."
    print "This program will exit after 15 seconds."
    stdout.flush()
    sleep(15)
    b.reset()
    print "Demo finished."

"""

from ctypes import cdll, CFUNCTYPE, POINTER, c_void_p, c_int, c_double, c_char

class GStimbox:
    """Create a connection to the g-STIMbox.

    The serial port number defaults to ``3``. A callback function
    can be specified that handles signals from the input
    connectors (see :ref:`gstimbox-usage-input`).

    """

    def __init__(self, port=3, callback=None):
        self.input_callback = callback
        try:
            self.dll = cdll.LoadLibrary("gSTIMbox")
        except WindowsError:
            raise GStimboxError("Could not find gSTIMbox.dll. Exiting...")
        if callback is not None:
            self.__register_input_callback(callback)
            r = self.dll.gSTIMboxinit(port, self.__cfunc_input_callback)
        else:
            r = self.dll.gSTIMboxinit(port)
        if (r != None):
            self.__device_handle = r
        else:
            raise GStimboxError("Could not connect to g-STIMbox.")

    def __del__(self):
        self.reset()
        self.close()

    def __input_callback(self, input_vector):
        r = [ord(input_vector[i]) for i in range(14)]
        self.__user_input_callback(r)

    def __register_input_callback(self, input_callback):
        if not callable(input_callback):
            raise TypeError("Argument input_callback must be callable.")
        self.__user_input_callback = input_callback
        # create C function
        self.__INPUT_CB_TYPE = CFUNCTYPE(c_void_p, POINTER(c_char))
        self.__cfunc_input_callback = \
            self.__INPUT_CB_TYPE(self.__input_callback)

    def reset(self):
        """Reset device."""
        r = self.dll.gSTIMboxreset(self.__device_handle)
        if (r != 1):
            raise GStimboxError("Could not disconnect from g-STIMbox.")

    def setMode(self, port, mode):
        """Set the operation mode of output ports.

        port is a list of port numbers to change (eg. ``[0, 2,
        3]``). Valid port numbers range from 0 to 15.

        modes is a list of modes for the ports defined in the port
        variable. A mode value can be either ``0`` (controlled
        manually, see portState()) or ``1`` (microprocessor controlled
        frequency, see setFrequency()).

        """
        num = len(port)
        if type(port) != list:
            raise TypeError("Argument port must be a list.")
        if type(mode) != list:
            raise TypeError("Argument mode must be a list.")
        if num != len(mode):
            raise ValueError(
                "Arguments port and mode must be of same length.")
        port_carr = (c_int * num)()
        mode_carr = (c_int * num)()
        for i in range(num):
            port_carr[i] = c_int(port[i])
            mode_carr[i] = c_int(mode[i])
        r = self.dll.gSTIMboxsetMode(
            self.__device_handle, num, port_carr, mode_carr)
        if (r != 1):
            raise GStimboxError("Could not set modes on g-STIMbox.")

    def setPortState(self, state):
        """Set ON/OFF state for ports running in mode ``0`` (see
        setMode()).

        state is a list with a length of 16. Valid values for a state
        is an integer of either ``0`` or ``1``.

        eg. ``state = [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]``

        """
        if type(state) != list:
            raise TypeError("Argument state must be a list.")
        if len(state) != 16:
            raise TypeError("Argument state must be of length 16.")
        state_carr = (c_int * 16)()
        for i in range(16):
            state_carr[i] = c_int(state[i])
        r = self.dll.gSTIMboxsetPortState(self.__device_handle, state_carr)
        if (r != 1):
            raise GStimboxError("Could not set port states on g-STIMbox.")

    def setFrequency(self, port, freq):
        """Set the frequencies for output ports.

        port - list of port numbers to change. Valid port numbers
        range from 0 to 15. (eg. ``[0, 6, 7]``)

        freq - list of frequencies which are to be assigned to the
        ports. Allowed values range from 1 to 50. The function rounds
        these frequencies to one digit after the comma. The length of
        ``freq`` must equal the length of port list. (eg. ``[1, 2.7,
        5.8]``)

        """
        num = len(port)
        if type(port) != list:
            raise TypeError("Argument port must be a list.")
        if type(freq) != list:
            raise TypeError("Argument freq must be a list.")
        if num != len(freq):
            raise ValueError(
                "Arguments port and freq must be of same length.")
        port_carr = (c_int * num)()
        freq_carr = (c_double * num)()
        for i in range(num):
            port_carr[i] = c_int(port[i])
            freq_carr[i] = c_double(freq[i])
        r = self.dll.gSTIMboxsetFrequency(
            self.__device_handle, num, port_carr, freq_carr)
        if (r != 1):
            raise GStimboxError("Could not set frequencies on g-STIMbox.")

    def close(self):
        """Close device connection."""
        r = self.dll.gSTIMboxclose(self.__device_handle)
        if (r != 1):
            raise GStimboxError("Could not disconnect from g-STIMbox.")

    def getHWVersion(self):
        """Returns firmware version."""
        fun = self.dll.gSTIMboxgetHWVersion
        fun.restype = c_double
        return fun()

    def getDriverVersion(self):
        """Returns API library version."""
        fun = self.dll.gSTIMboxgetDriverVersion
        fun.restype = c_double
        return fun()


class GStimboxError(Exception):
    """g-STIMbox device communication error."""
    pass
