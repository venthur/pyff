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

class PluginController(object):
    
    #
    # TODO: Problem with path
    #
    
    """Finds, loads and unloads plugins."""
    
    def __init__(self, plugindirs, baseclass, initparams=None):
        self.plugindirs = plugindirs
        self.baseclass = baseclass
        self.initparams = initparams
        self.availablePlugins = dict()
        self.oldModules = None
        
        # FIXME: Does not quite work as expected
        for dir in plugindirs:
            if os.path.exists(dir):
                dir = os.path.normpath(dir)
                sys.path.append(dir)
            else:
                print "Path %s does not exist!"
            for i in sys.path: print i
                
        


    def test_plugin(self, root, filename):
        """Test if given module contains a valid plugin instance.
        
        Returns None if not or (name, modulename) otherwise."""

        for plugindir in self.plugindirs:
            if root.startswith(plugindir):
                root = root.replace(plugindir, "")
        
        module = root + os.sep + filename
        if module.lower().endswith(".py"):
            module = module[:-3]
        module = os.path.normpath(module)
        module = module.replace(os.sep, ".")
        while module.startswith("."):
            module = module[1:]
        
#        # WTF? 
#        if self.additionalFBPath:
#            modPath = self.additionalFBPath.replace(os.sep, ".")
#            root = root.replace(modPath, "")
        
        # try to import
        try:
            name = module.split(".")[-1]
            print "***", module, name
            mod = __import__(module, fromlist=[None])
            #print "1/3: loaded module (%s)." % str(module)
            plugin = getattr(mod, name)(None)
            #print "2/3: loaded feedback (%s)." % str(name)
            if isinstance(plugin, self.baseclass):
                #print "3/3: feedback is valid Feedback()"
                return name, module
        except:
            print traceback.format_exc()
            raise ImportError("Invalid Plugin")

    def find_plugins(self):
        """Returns a list of available plugins."""
        for plugindir in self.plugindirs:
            for root, dirs, files in os.walk(plugindir):
                for filename in files:
                    if filename.lower().endswith(".py"):
                        # ok we found a candidate, check if it's a valid feedback
                        try:
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
        try:
            mod = __import__(name, fromlist=[None])
            plugin = getattr(mod, name)(self.initparams) if self.initparams else getattr(mod, name)()
        except:
            raise ImportError("Unable to load Plugin %s" % str(name))
    
    def unload_plugin(self):
        """Unload currently loaded plugin."""
        if not self.oldModules:
            return
        for mod in sys.modules.keys():
            if not self.oldModules.haskey(mod):
                del sys.modules[mod]
        self.oldModules = None
        

        
def main():
    import FeedbackBase.Feedback
    pc = PluginController(["../Feedbacks", "../../../pyff-tu/src/Feedbacks"], FeedbackBase.Feedback.Feedback)
    pc.find_plugins()
    for key in pc.availablePlugins: print key

if __name__ == "__main__":
    main()
    