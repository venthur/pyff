# feedbackprocesscontroller.py -
# Copyright (C) 2009-2011  Bastian Venthur
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


from threading import Thread
import logging
import asyncore
from multiprocessing import Process, Event

from lib.PluginController import PluginController
import lib.PluginController
import ipc


class FeedbackProcess(Process):
    """Process that wrapps the Feedback's activities."""

    def __init__(self, modname, classname, ipcReady, port):
        Process.__init__(self)
        self.classname = classname
        self.modname = modname
        self.ipcReady = ipcReady
        self.port = port
        self.loglevel = logging.getLogger().level
        self.fbloglevel = logging.getLogger("FB").level
        self.logformat = logging.getLogger().handlers[0].formatter._fmt


    def run(self):
        """Run the FeedbackProcess' activities in the new process."""
        # We're in a new process
        reload(lib.PluginController)
        try:
            fbClass = lib.PluginController.import_module_and_get_class(self.modname, self.classname)
        except:
            # Loading the class somehow failed.
            logging.exception("Loading the module/class failed, this might help to track down the problem:")
            self.ipcReady.set()
            return
        # Re-initialize logger for this process
        logging.basicConfig(level=self.loglevel, format=self.logformat)
        logging.getLogger("FB").setLevel(self.fbloglevel)
        feedback = fbClass(port_num=self.port)
        feedback.logger.debug("Initialized Feedback.")

        # Start the Feedbacks IPC Channel
        asyncore.socket_map.clear()
        conn = ipc.get_feedbackcontroller_connection()
        ipc.FeedbackIPCChannel(conn, feedback)
        feedback.logger.debug("Starting IPC loop.")
        fbipcthread = Thread(target=ipc.ipcloop)
        fbipcthread.start()
        self.ipcReady.set()
        # Start the Feedbacks Mainloop
        try:
            feedback.on_init()
            feedback._playloop()
        finally:
            feedback.logger.debug("Closing IPC socket.")
            conn.close()


class FeedbackProcessController(object):
    """Takes care of starting and stopping of Feedback Processes."""

    def __init__(self, plugindirs, baseclass, timeout):
        """Initialize the Feedback Process Controller."""
        # Where are we:
        # Proc/Thread: FB/??
        self.logger = logging.getLogger("FeedbackProcessController")
        self.currentProc = None
        self.timeout = timeout
        self.pluginController = PluginController(plugindirs, baseclass)

        self.pluginController.find_plugins()
        self.pluginController.unload_plugin()


    def start_feedback(self, name, port):
        """Starts the given Feedback in a new process.

        :param name: Feedback
        :type name: str
        :param port: Parallel Port

        """
        self.logger.debug("Starting new Process...",)
        if self.currentProc:
            self.logger.warning("Trying to start feedback but another one is still running. Killing the old one now and proceed.")
            self.stop_feedback()
        ipcReady = Event()
        self.currentProc = FeedbackProcess(self.pluginController.availablePlugins[name], name, ipcReady, port)
        self.currentProc.start()
        # Wait until the network from the Process is ready, this is necessary
        # since spawning a new process under Windows is very slow.
        self.logger.debug("Waiting for IPC channel to become ready...")
        ipcReady.wait()
        self.logger.debug("IPC channel ready.")
        self.logger.debug("Done starting process.")


    def stop_feedback(self):
        """Stops the current Process.

        First it tries to join the process with the given timeout, if that fails
        it terminates the process the hard way.
        """
        self.logger.debug("Stopping process...",)
        if not self.currentProc:
            self.logger.debug("No process running, nothing to do.")
            return

        self.currentProc.join(self.timeout)
        if self.currentProc.is_alive():
            self.logger.warning("Process still alive, terminating it...",)
            self.currentProc.terminate()
            self.currentProc.join(self.timeout)
            if self.currentProc.is_alive():
                self.logger.error("Process still alive, giving up.")

        del(self.currentProc)
        self.currentProc = None
        self.logger.debug("Done stopping process.")


    def get_feedbacks(self):
        """Return a list of available Feedbacks.

        :returns: List of available feedbacks

        """
        return self.pluginController.availablePlugins.keys()

