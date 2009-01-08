class PluginController(object):
    """Finds, loads and unloads plugins."""
    
    def __init__(self, plugindirs, baseclass, initparams=None):
        self.plugindirs = [plugindirs]
        self.baseclass = baseclass
        self.initparams = initparams
        self.availablePlugins = dict()
        self.oldModules = None

    def test_plugin(self, root, file):
        """Test if given module contains a valid plugin instance.
        
        Returns None if not or (name, modulename) otherwise."""
        module = root + os.sep + file
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
            mod = __import__(module, fromlist=[None])
            print "1/3: loaded module (%s)." % str(module)
            plugin = getattr(mod, name)(None)
            print "2/3: loaded feedback (%s)." % str(name)
            if isinstance(plugin, self.baseclass):
                print "3/3: feedback is valid Feedback()"
                return name, module
        except:
            raise ImportError("Invalid Plugin")

    def find_plugins(self):
        """Returns a list of available plugins."""
        for plugindir in self.plugindirs:
            for root, dirs, files in os.walk(plugindir):
                print root, dirs, files
                for file in files:
                    if file.lower().endswith(".py"):
                        # ok we found a candidate, check if it's a valid feedback
                        try:
                            name, module = self.test_plugin(root, file)
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
        
        

        
def main2():
    import FeedbackBase.Feedback
    pc = PluginController("Feedbacks", FeedbackBase.Feedback.Feedback)
    pc.find_plugins()
    print "=================="
    print pc.availablePlugins
