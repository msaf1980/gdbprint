[ -z ${GDB_PYTHON} ] && {
    echo "incorrect GDB_PYTHON" >&2
    exit 1
}
${GDB_PYTHON} setup.py test || exit 1
${GDB_PYTHON} setup.py install --user || exit 1
${GDB_PYTHON} setup.py bdist || exit 1
