# test_rollbackimporter.py -
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


import unittest
import sys

from lib.RollbackImporter import RollbackImporter


class RollbackImporterTestCase(unittest.TestCase):
    
    def testSimpleImport(self):
        """Should remove simple import."""
        modname = "lib.test.mod_wo_imports"
        self._del_if_existent(modname)
        rbi = RollbackImporter()
        import lib.test.mod_wo_imports
        self.assertTrue(sys.modules.has_key(modname))
        rbi.uninstall()
        self.assertFalse(sys.modules.has_key(modname))
        
    def testComplexImport(self):
        """Should remove import and import(s) of import."""
        modname1 = "lib.test.mod_w_imports"
        modname2 = "lib.test.mod_wo_imports"
        self._del_if_existent(modname1)
        self._del_if_existent(modname2)
        rbi = RollbackImporter()
        import lib.test.mod_w_imports
        self.assertTrue(sys.modules.has_key(modname2))
        rbi.uninstall()
        self.assertFalse(sys.modules.has_key(modname2))
        
    def testRelativeImport(self):
        """Should remove relative import."""
        modname = "lib.test.mod_wo_imports"
        self._del_if_existent(modname)
        rbi = RollbackImporter()
        import mod_wo_imports
        self.assertTrue(sys.modules.has_key(modname))
        rbi.uninstall()
        self.assertFalse(sys.modules.has_key(modname))
        
    def testSysModulesEqualBeforeAndAfter(self):
        """Modules before and after usage of RBI should be equal."""
        before = sys.modules.copy()
        rbi = RollbackImporter()
        import mod_w_imports
        rbi.uninstall()
        self.assertEqual(before, sys.modules)
        
    def _del_if_existent(self, modname):
        if sys.modules.has_key(modname):
            del(sys.modules[modname])

        
#suite = unittest.makeSuite(BcixmlTestCase)
def suite():
    testSuite = unittest.makeSuite(RollbackImporterTestCase)
    return testSuite

def main():
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
if __name__ == "__main__":
    main()
    