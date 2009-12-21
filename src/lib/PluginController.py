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
import traceback
import logging


def import_module_and_get_class(modname, classname):
    """Import the module and return modname.classname."""
    try:
        mod = __import__(modname, fromlist=[None])
        return getattr(mod, classname)
    # FIXME: is this exception usefull? it is at least wrong since it does
    # throws and import error even if import succeeded
    except:
        raise ImportError("Unable to load class %s from module %s" % (str(classname), str(modname)))


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


    def test_plugin(self, root, filename):
        """Test if given module contains a valid plugin instance.
        
        Returns None if not or (name, modulename) otherwise."""
        module = root + os.sep + filename
        if module.lower().endswith(".py"):
            module = module[:-3]
        module = os.path.normpath(module)
        module = module.replace(os.sep, ".")
        while module.startswith("."):
            module = module[1:]
        
        # try to import
        self.logger.debug("Testing plugin: %s" % str(module))
        try:
            name = module.split(".")[-1]
            mod = __import__(module, fromlist=[None])
            self.logger.debug("... loaded module: %s." % str(module))
            plugin = getattr(mod, name)
            self.logger.debug("... loaded plugin: %s." % str(name))
            if not issubclass(plugin, self.baseclass):
                raise ImportError("Invalid Subclass")
            self.logger.debug("... is subclass: %s." % str(name))
            return name, module
        except:
            self.logger.debug(traceback.format_exc())
            raise ImportError("Invalid Plugin")


    def find_plugins(self):
        """Returns a list of available plugins."""
        for plugindir in self.plugindirs:
            for root, dirs, files in os.walk(plugindir):
                for filename in files:
                    if filename.lower().endswith(".py"):
                        # ok we found a candidate, check if it's a valid feedback
                        try:
                            if root.startswith(plugindir):
                                root = root.replace(plugindir, "", 1)
                            name, module = self.test_plugin(root, filename)
                            self.availablePlugins[name] = module
                        except ImportError:
                            pass

        
    def load_plugin(self, name):
        """Loads the given plugin and unloads possibly sooner loaded plugins."""
        if self.oldModules:
            self.unload_plugin()
        self.oldModules = sys.modules.copy()
        if not self.availablePlugins.has_key(name):
            raise ImportError("Plugin %s not available" % str(name))
        myclass = import_module_and_get_class(self.availablePlugins[name], name)
        return myclass

    
    def unload_plugin(self):
        """Unload currently loaded plugin."""
        if self.oldModules:
            for mod in sys.modules.keys():
                if not self.oldModules.has_key(mod):
                    del sys.modules[mod]
            self.oldModules = None

        
def main():
    import FeedbackBase.Feedback
    pc = PluginController(["../Feedbacks", "../../../pyff-tu/src/Feedbacks"], FeedbackBase.Feedback.Feedback)
    pc.find_plugins()
    for key in pc.availablePlugins: print key, pc.availablePlugins[key]

if __name__ == "__main__":
    main()

