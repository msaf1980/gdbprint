import sys
import gdb
if sys.version_info < (3, 0, 0):
    import printcfg
else:
    from . import printcfg

def print_str(s):
    gdb.write(s)

# Starting with the type ORIG, search for the member type NAME.  This
# handles searching upward through superclasses.  This is needed to
# work around http://sourceware.org/bugzilla/show_bug.cgi?id=13615.
def find_type(orig, name):
    typ = orig.strip_typedefs()
    while True:
        # Strip cv-qualifiers.  PR 67440.
        search = '%s::%s' % (typ.unqualified(), name)
        #print("SEARCH " + search)
        try:
            return gdb.lookup_type(search)
        except RuntimeError:
            pass
        # The type was not found, so try the superclass.  We only need
        # to check the first superclass, so we don't bother with
        # anything fancier here.
        field = typ.fields()[0]
        if not field.is_base_class:
            raise ValueError("Cannot find type %s::%s" % (str(orig), name))
        typ = field.type

def typecode_strip(nvalue):
    try:
        typecode = nvalue.dynamic_type.unqualified().strip_typedefs()
    except Exception as e:
        typecode = nvalue.type
    return typecode

def is_iter_typecode(typecode):
    if typecode in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_FLT, gdb.TYPE_CODE_DECFLOAT, 
            gdb.TYPE_CODE_PTR, gdb.TYPE_CODE_CHAR):
        return True
    else:
        return False

_type_name_ = {
    gdb.TYPE_CODE_PTR : "pointer",
    gdb.TYPE_CODE_ARRAY : "array",
    gdb.TYPE_CODE_STRUCT : "structure",
    gdb.TYPE_CODE_UNION : "union",
    gdb.TYPE_CODE_ENUM : "enum",
    gdb.TYPE_CODE_FLAGS : "bit_flags_type",
    gdb.TYPE_CODE_FUNC : "function",
    gdb.TYPE_CODE_INT : "integer",
    gdb.TYPE_CODE_FLT : "float",
    gdb.TYPE_CODE_VOID : "void",
    gdb.TYPE_CODE_SET : "set",
    gdb.TYPE_CODE_RANGE : "range",
    gdb.TYPE_CODE_STRING : "string",
    gdb.TYPE_CODE_BITSTRING : "bitstring",
    gdb.TYPE_CODE_ERROR : "unknown",
    gdb.TYPE_CODE_METHOD : "method",
    gdb.TYPE_CODE_METHODPTR : "methodptr",
    gdb.TYPE_CODE_MEMBERPTR : "memberptr",
    gdb.TYPE_CODE_REF : "reference",
    gdb.TYPE_CODE_CHAR : "char",
    gdb.TYPE_CODE_BOOL : "bool",
    gdb.TYPE_CODE_COMPLEX : "complex",
    gdb.TYPE_CODE_TYPEDEF : "typedef",
    gdb.TYPE_CODE_NAMESPACE : "namespace",
    gdb.TYPE_CODE_DECFLOAT : "decfloat",
    gdb.TYPE_CODE_INTERNAL_FUNCTION : "internal_function"
}

try:
    _type_name_[gdb.TYPE_CODE_RVALUE_REF] = "rvalue"
except:
    pass


def typename(gdbtype):
    try:
        return _type_name_[gdbtype]
    except:
        return "unknown %s" % str(gdbtype)

def char_unsign(nvalue):
    c = int(nvalue)
    if c < 0:
        return c + 256
    else:
        return c

def char_to_string(nvalue, cp = None):
    #print(str(nvalue))
    c = char_unsign(nvalue)
    if c == 0:
        return str(c) + " \"0x0\""
    elif sys.version_info < (3, 0, 0):
        if not cp is None and cp != "utf-8":
            return str(c) + " \"" + chr(c).decode(cp) + "\""
        else:
            return str(c) + " \"" + chr(c).decode(printcfg.codepage_failback) + "\""
    else:
        if not cp is None and cp != "utf-8":
            return str(c) + " \"" + c.to_bytes(1, byteorder='big').decode(cp) + "\""
        else:
            return str(c) + " \"" + c.to_bytes(1, byteorder='big').decode(printcfg.codepage_failback) + "\""

def wchar_to_string(code):
    if sys.version_info < (3, 0, 0):
        return str(code) + ' L\'' + str(unichr(code)) + '\''
    else:
        return str(code) + ' L\'' + str(chr(code)) + '\''
