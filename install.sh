#!/bin/sh

GDB=`which gdb`
GDB_PYTHON=`ldd ${GDB} | grep libpython | awk '{ print $1; }' | sed -e 's/\.so.*//g' -e 's/libpython/\/usr\/bin\/python/g'`

${GDB_PYTHON} setup.py install $@
