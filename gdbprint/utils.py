import traceback
import sys
from .gdbutils import print_str
#if sys.version_info < (3, 0, 0):
#    import printcfg
#else:
from . import printcfg
from .define import basestr
from .printcfg import debugprinters, debugprinters_typenames


class DisplayType:
    NONE = -1
    RAW = 0
    RAW_S = "raw"
    ARRAY = 1
    ARRAY_S = "array"
    STRING = 2
    STRING_S = "string"
    LIST = 3
    LIST_S = "list"
    LIST_SIZED = 4
    LIST_SIZED_S = "list_sized"
    STRUCT = 5
    STRUCT_S = "struct"
    SUBTYPE = 6
    SUBTYPE_S = "subtype"
    SET = 7
    SET_S = "set"    
    MAP = 8
    MAP_S = "map"
    BITSET = 9
    BITSET_S = "bitset"
    PTR = 10
    PTR_S = "pointer"
    
    def __init__(self,  s):
        if s in (self.ARRAY, self.ARRAY_S):
            self.value = self.ARRAY
            self.str = self.ARRAY_S
        elif s in (self.STRING, self.STRING_S):
            self.value = self.STRING
            self.str = self.STRING_S
        elif s in (self.STRUCT, self.STRUCT_S):
            self.value = self.STRUCT
            self.str = self.STRUCT_S
        elif s in (self.SUBTYPE, self.SUBTYPE_S):
            self.value = self.SUBTYPE
            self.str = self.SUBTYPE_S
        elif s in (self.LIST, self.LIST_S):
            self.value = self.LIST
            self.str = self.LIST_S
        elif s in (self.LIST_SIZED, self.LIST_SIZED_S):
            self.value = self.LIST_SIZED
            self.str = self.LIST_SIZED_S
        elif s in (self.SET, self.SET_S):
            self.value = self.SET
            self.str = self.SET_S
        elif s in (self.MAP, self.MAP_S):
            self.value = self.MAP
            self.str = self.MAP_S
        elif s in (self.BITSET, self.BITSET_S):
            self.value = self.BITSET
            self.str = self.BITSET_S
        elif s in (self.RAW, self.RAW_S):
            self.value = self.RAW
            self.str = self.RAW_S
        elif s in (self.PTR, self.PTR_S):
            self.value = self.PTR
            self.str = self.PTR_S
        else:
            self.value = self.NONE
            if s is None:
                self.str = ""
            else:
                self.str = str(s)
    
    def __int__(self):
        return self.value
        
    def __str__(self):
        return self.str
        
    def __eq__(self, y):
        return self.value==y.value


def register_printer(obj):
    if hasattr(obj,  'names'):
        for name in obj.names:
            debugprinters[name] = obj
    if hasattr(obj,  'typename'):
        debugprinters_typenames[obj.typename] = obj

#def register_printer_type(name,  typename):
 #   debugprinters_typemap[name] = typename
 
def resolve_printer(name):
    return debugprinters.get(name)

def resolve_printer_typename(typename):
    return debugprinters_typenames.get(typename)

def show_printers():
    try:
        if len(debugprinters) > 0:
            print_str("Debug printers:\n")
            for k in debugprinters:
                v = debugprinters[k]
                print_str("\"%s\" = \"%s\" (%s)\n" % (k, str(v), str(DisplayType(v.display_hint()))))

            if len(debugprinters_typenames) > 0:
                print_str("\n")

        if len(debugprinters_typenames) > 0:
            print_str("Debug printers typenames:\n")
            for k in debugprinters_typenames:
                v = debugprinters_typenames[k]
                print_str("\"%s\" = \"%s\" (%s)\n" % (k, str(v), str(DisplayType(v.display_hint()))))
    except:
        print_str(traceback.format_exc())

def is_true(str):
    if str in [ "y", "yes", "true", "on" ]:
        return True
    else:
        return False

def is_true_or_num(str):
    if str in [ "y", "yes", "true", "on" ]:
        return 1
    elif str in [ "n", "no", "false", "off" ]:
        return 0
    else:
        return int(str)

def error_format(e):
    if printcfg.debug or e is None:
        s = traceback.format_exc()
    else:
        s = str(e)
    return s

def print_debug(s, level = 1):
    if level <= printcfg.debug and not s is None:
        print_str(s)
        print_str("\n")

def print_warn(s):
    if not s is None:
        print_str("WARNING: " + s)
        print_str("\n")

def print_error(s):
    if not s is None:
        print_str("ERROR: " + str)
        print_str("\n")

def print_obj(s, indent = ""):
    if s is None:
        print_str("None\n")
    elif  isinstance(s, basestr):
        print_str("%s\n" % s)
    elif  isinstance(s, (tuple, list, set)):
        #print_str("[ %s ]\n" % ", ".join(s))
        print_str("[ ")
        for v in s:
            print_obj(v, indent + "  ")
            print_str(", ")
        print_str("]\n")
    elif hasattr(s, '__dict__'):
        attrs = dir(s)
        if indent != "":
            print_str("\n")
        print_str("%s(\n" % indent)
        for i in attrs:
            if i.startswith("__"):
                continue
            v = getattr(s, i)
            if not callable(v):
                print_str("%s%s = " % (indent, i))
                print_obj(v, indent + " ")
        print_str("%s)\n" % indent)
    else:
        print_str("%s\n" % str(s))


def wchar_to_string(code):
    if sys.version_info < (3, 0, 0):
        return str(code) + ' L\'' + str(unichr(code)) + '\''
    else:
        return str(code) + ' L\'' + str(chr(code)) + '\''
 
