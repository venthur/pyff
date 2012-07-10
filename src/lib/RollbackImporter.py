# RollbackImporter.py - inspired by RollbackImporter from pyunit.sf.net
# Copyright (C) 2008-2009  Bastian Venthur
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


import __builtin__
import sys


class RollbackImporter(object):
    """
    RollbackImporter.

    RollbackImporter instances install themselves as a proxy for the built-in
    :func:`__import__` function that lies behind the 'import' statement. Once
    installed, they note all imported modules, and when uninstalled, they
    delete those modules from the system module list; this ensures that the
    modules will be freshly loaded from their source code when next imported.

    Usage::

        if self.rollbackImporter:
            self.rollbackImporter.uninstall()
        self.rollbackImporter = RollbackImporter()
        # import some modules

    """

    def __init__(self):
        """Init the RollbackImporter and setup the import proxy."""
        self.oldmodules = sys.modules.copy()
        self.realimport = __builtin__.__import__
        __builtin__.__import__ = self._import

    def uninstall(self):
        """Unload all modules since __init__ and restore the original import."""
        for module in sys.modules.keys():
            if not self.oldmodules.has_key(module):
                del sys.modules[module]
        __builtin__.__import__ = self.realimport

    def _import(self, name, globals={}, locals={}, fromlist=[], level=-1):
        """Our import method."""
        return apply(self.realimport, (name, globals, locals, fromlist, level))

