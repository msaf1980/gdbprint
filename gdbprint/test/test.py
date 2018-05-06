#!/usr/bin/python

import sys
# unittest init for different python version
if sys.version_info[0] >= 3:
    import unittest
elif sys.version_info[0] == 2:
    if sys.version_info[1] >= 7:
        import unittest
    else
        import unittest2
    assertCountEqual = assertItemsEqual
# end unittest init for different python version

import parser

class CommandParser(unittest.TestCase):
    def setUp(self):
        self.cmd_parse = CommandParser()

    def test_add(self):
        self.assertEqual(calc.add( 1 , 2 ), 3 )


if _name__ == '__main__' :
    unittest.main()

