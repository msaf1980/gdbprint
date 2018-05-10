from __future__ import print_function

import gdb
import sys
from .gdbutils import print_str

class OutType:
    TEXT = 0
    NAMED = 1

    @staticmethod
    def from_str(out_type):
        l = out_type.lower()
        if l in ("t", "text"):
            return OutType.TEXT
        elif l in ("n", "named"):
            return OutType.NAMED
        else:
            raise ValueError("unknown output type %s" % out_type)
 
    @staticmethod
    def to_str(out_type):
        if out_type == OutType.TEXT:
            return "text"
        elif out_type == OutType.NAMED:
            return "named"
        else:
            return "unknown (%d)" % out_type
 

out_type = OutType.TEXT
debug = 0
#xml = False
#pygdbmi = False
fetch_array = 50
fetch_string = 400
codepage_default = "1251"
codepage = codepage_default
codepage_failback = codepage_default
depth = 2
width = 80
#cwidth = 30

#p_tree = None
verbose = 2 
indent_pre = "    "

# Dict   name : obj
debugprinters = {}

# Dict   typename : obj
debugprinters_typenames = {}

# Dict   name : typename
#debugprinters_typemap = {}

def help():
    cmd_opt = "p_s"
    print_str("Options:\n")
    print_str("out_type is " + OutType.to_str(out_type) + " # Set output type (%s [output_type | o] [text | named]\n" % cmd_opt)
    print_str("debug is " + str(debug) + " # Enable debug output (%s [debug | d] [(1 | yes | y | true | on) (0 | no | n | false | off)] (N)\n" % cmd_opt)
    print_str("fetch array is " + str(fetch_array) + " # Default fetch array size (%s [fetch array | f a] SIZE)\n" % cmd_opt)
    print_str("fetch string is " + str(fetch_string) + " # Default fetch string size (%s [fetch string | f s] SIZE)\n" % cmd_opt)
    print_str("codepage is " + str(codepage) + " # Codepage for single-byte (char) string (%s [codepage | cp] CODEPAGE [CODEPAGE_FAILBACK]\n" % cmd_opt)
    print_str("failback codepage is " + str(codepage_failback) + " # Codepage for single-byte (char) string. Used if codepage is UTF and conversion failed\n")    
    print_str("verbose is " + str(verbose) + " # Verbose Output (%s [verbose | v] [0 | 1 | 2]), 0 - only value, 1 - print type, 2 - print length, 3 - also print full type (for STL)\n" % cmd_opt)
    print_str("width is " + str(width) + " # Row width for display simple arrays (%s [width | w] WIDTH\n" % cmd_opt)
    print_str("depth is " + str(depth) + " # Depth for expand complex structuras in arrays and list (%s [depth | de] DEPTH)\n" % cmd_opt)

    print_str("\n%s [p | printers] # Show registered printers\n\n" % cmd_opt)

    print_str("p_v EXPR1 ; EXPR2 ; .. # Print variables by expression evaluate\n")
