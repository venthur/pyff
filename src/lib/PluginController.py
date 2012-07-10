# PluginController.py -
# Copyright (C) 2009  Bastian Venthur
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


import sys
import os
import logging


def import_module_and_get_class(modname, classname):
    """Import the module and return modname.classname.

    :param modname: Module name
    :type modname: str
    :param classname: Class name
    :type classname: str

    """
    mod = __import__(modname, fromlist=[None])
    return getattr(mod, classname)


class PluginController(object):
    """Finds, loads and unloads plugins."""


    def __init__(self, plugindirs, baseclass):
        self.logger = logging.getLogger("PluginController")
        self.plugindirs = map(os.path.normpath, map(os.path.abspath, plugindirs))
        self.baseclass = baseclass
        self.availablePlugins = dict()
        self.oldModules = None

        for dir in plugindirs:
            if os.path.exists(dir):
                sys.path.append(dir)
            else:
                self.logger.warning("Path %s does not exist, ignoring it" % str(dir))


    def find_plugins(self):
        """Find Plugins.

        :returns: list of available plugins.

        """
        for plugindir in self.plugindirs:
            for root, dirs, files in os.walk(plugindir):
                if 'feedbacks.list' in files:
                    self.logger.info("Found feedbacks.list in %s" % root)
                    del dirs[:]
                    fbdict = self.load_feedback_list(root+os.path.sep+'feedbacks.list', plugindir)
                    for fb, module in fbdict.iteritems():
                        self.availablePlugins[fb] = module
                    continue


    def load_feedback_list(self, filename, plugindir):
        """Load classnames from file and construct modulename relative to
        plugindir from plugindir, filename and file entries.

        :param filename: filename
        :type filename: str
        :param plugindir: Plugin directory
        :type plugindir: str
        :returns: dictionary: classname -> module.

        """
        # Read the lines from file
        fh = open(filename, "r")
        lines = fh.readlines()
        fh.close()
        # Construct absolute module name from plugindir, filename and file entry
        base = os.path.dirname(filename)
        base = base.replace(plugindir, "", 1)
        base = base.split(os.path.sep)
        fbdict = dict()
        for line in lines:
            line = line.strip()
            # Ignore empty lines or comments
            if len(line) == 0 or line.startswith("#"):
                continue
            line = line.split(".")
            full_path_to_class = base + line
            while("" in full_path_to_class):
                full_path_to_class.remove("")
            fbdict[full_path_to_class[-1]] = ".".join(full_path_to_class[:-1])
        return fbdict


    def unload_plugin(self):
        """Unload currently loaded plugin."""
        if self.oldModules:
            for mod in sys.modules.keys():
                if not self.oldModules.has_key(mod):
                    del sys.modules[mod]
            self.oldModules = None


def main():
    import sys
    #sys.path.append("../")
    import FeedbackBase.Feedback
    pc = PluginController(["../Feedbacks", "../../../pyff-tu/src/Feedbacks"], FeedbackBase.Feedback.Feedback)
    pc.find_plugins()
    for key in pc.availablePlugins:
        print key, pc.availablePlugins[key]

if __name__ == "__main__":
    main()

