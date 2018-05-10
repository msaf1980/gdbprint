import sys

if sys.version_info < (3, 0, 0):
    uchr = unichr
    basestr = basestring
    longx = long
else:
    uchr = chr
    basestr = (str, bytes)
    longx = int
