(gdb) file test
(gdb) py sys.path.append('..')
(gdb) py import gdbprint
(gdb) break 74
(gdb) run
Breakpoint: file test.cpp, line 74.

Breakpoint 1, main at test.cpp:74

(gdb) p_s verbose 2
(gdb) p_s w 0
