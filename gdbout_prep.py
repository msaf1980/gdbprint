#!/usr/bin/python

import sys, os, re

for o in sys.stdin:
    if not o.startswith('(gdb) '):
	cdir = os.path.dirname(os.path.realpath(__file__))
        o = re.sub(r'(=.*) 0x[0-9a-f]+', r'\1 0xXXXXX', o)
        o = re.sub(r'Temporary breakpoint 1 at .*\n', '', o)
        o = re.sub(r'Breakpoint [0-9]+ at 0x[0-9a-f]+:', 'Breakpoint:', o)
        o = re.sub(r'Breakpoint [0-9]+, main \(argc=1, argv=0x[0-9a-f]+\) at', 'Breakpoint 1, main at', o)
        o = re.sub(r'[0-9]+[ \t]+return 0;', '', o)
        o = re.sub(r'0x[0-9a-f]*[1-9a-f]+[0-9a-f]*', '0xHEX', o)
        o = re.sub(cdir, '', o)
	
    sys.stdout.write(o)
