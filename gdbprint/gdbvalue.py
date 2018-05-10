import sys
import gdb
import re
import traceback
if sys.version_info < (3, 0, 0):
    import gdbutils
    import printcfg
else:
    from . import gdbutils
    from . import printcfg
from .define import longx
from .printcfg import OutType
from .gdbutils import print_str
from .gdbutils import char_to_string, char_unsign, typename
from .utils import print_debug, error_format
from .gdbprinters import read_string, read_unicode
from .gdbprinters import short_name, p_name
from .utils import DisplayType
from .utils import print_debug, print_warn, print_error, print_obj
from .utils import resolve_printer, resolve_printer_typename
from .parser import filters_check
from .parser import calc_range
from .parser import Filter, CmpVal, FType, Transform, Range, Mod, ValueOut, SubType

def calc_cwidth(vtype):
    cwidth = 0
    if str(vtype) in ('char', 'signed char', 'unsigned char'):
        num_type = 1
    elif str(vtype) == 'wchar_t':
        num_type = 2
    else:
        if vtype.code == gdb.TYPE_CODE_BOOL:
            num_type = 0
            cwidth = 6 + len(str(sys.maxsize))
        elif vtype.code == gdb.TYPE_CODE_INT:
            num_type = 0
            cwidth = 6 + len(str(sys.maxsize))
            #cwidth = 6 + len(str(sys.maxsize)) + len(str(sys.maxint))
        elif vtype.code == gdb.TYPE_CODE_FLT:
            num_type = 0
            cwidth = 6 + len(str(sys.maxsize))
        else:
            num_type = -1

    return (num_type, cwidth)


class GdbValue:
    p_ptr_cast = re.compile("( *\* *)+$")

    def __init__(self, s):
        self.t = FType.VAL
        self.v = s

        self.vtype = gdbutils.typecode_strip(self.v) # Variable type. For GDB type check vtype.cod

    # Check against Filter
    def check(self, f):
        if f.stopkey:
            action = Filter.STOP
        else:
            action = Filter.PASS
        for fi in f.fi:
            if fi.c1.t == FType.THIS:
                if self.vtype.code in (gdb.TYPE_CODE_INT, gdb.TYPE_CODE_FLT, gdb.TYPE_CODE_PTR) and \
                        fi.c2.t == FType.NUM:
                    if str(self.vtype) in ('char', 'signed char', 'unsigned char'):
                        v = char_unsign(self.v)
                    elif self.vtype.code == gdb.TYPE_CODE_FLT:
                        v = float(self.v)
                    else:
                        v = longx(self.v)
                    if fi.cmp_v == CmpVal.EQ:
                        if v == fi.c2.v:
                            return action
                    elif fi.cmp_v == CmpVal.NE:
                        if v != fi.c2.v:
                            return action
                    elif fi.cmp_v == CmpVal.GT:
                        if v > fi.c2.v:
                            return action
                    elif fi.cmp_v == CmpVal.GE:
                        if v >= fi.c2.v:
                            return action
                    elif fi.cmp_v == CmpVal.LT:
                        if v < fi.c2.v:
                            return action
                    elif fi.cmp_v == CmpVal.LE:
                        if v <= fi.c2.v:
                            return action
                    else:
                        raise ValueError("unsupported comparator %d for %d and %s" % (fi.cmp_v, self.vtype.code, str(fi.c2)))
                else:
                    raise ValueError("unsupported type for filter")
            elif fi.c1.t == FType.NAME:
                raise ValueError("filter name check not supported: '%s'" % fi.c1.v)
            else:
                raise ValueError("filter type check not supported: '%s' (%d)" % (str(fi.c1.v), fi.c1.t))

        if f.stopkey:
            return Filter.PASS
        else:
            return Filter.SKIP
 

    def deref(self):
        return GdbValue(self.v.dereference())

    def ref(self):
        return GdbValue(self.v.referenced_value())


    def cast(self, cast):
        try:
            m = self.p_ptr_cast.search(cast)
            if m is None:
                cast_t = gdb.lookup_type(cast)
            else:
                r = m.span()[0]
                i = r
                c = 0
                i = cast.find("*", r)

                while i > 0:
                    c += 1
                    i = cast.find("*", i + 1)
                    cast_deref = cast[0:r]
                    cast_t = gdb.lookup_type(cast_deref)

                while c > 0:
                    cast_t = cast_t.pointer()
                    c -= 1
            return GdbValue(self.v.cast(cast_t))
        except Exception as e:
            if printcfg.debug:
                raise ValueError("<unresolve to '" + cast + "': " + traceback.format_exc() + ">")
            else:
                raise ValueError("<unresolve to '" + cast + "': " + str(e) + ">")

    def print_v(self, name, depth, expr, pos, print_name = True, print_head = True, indent = "", mod = None):
        self.value = ValueOut()

        if print_name:
            self.value.name = name
            self.value.print_name(indent)

        try:
            if print_head or str(self.vtype) == "void *":
                if printcfg.verbose > 2:
                    self.value.typename = str(self.vtype)
                else:
                    self.value.typename = p_name(str(self.vtype))

            if self.v.address == 0:
                self.value.address = self.v.address
                self.value.print_value()
                return

            if self.v.is_optimized_out:
                self.value.value = "<optimized_out>"
                self.value.print_value()
                return

            if mod is None:
                mod = Mod()
                pos = mod.get_transform(expr, pos)

            if not mod.transform is None and mod.transform.v == Transform.SIMPLE:
                self.value.value = str(self.v)
                self.value.print_value()
            elif self.vtype.code in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION):
                if print_head:
                    self.value.address = self.v.address

                #self.value.print_value()
                self.print_struct(depth, expr, pos, indent, mod)
                return
            elif str(self.vtype) in ('char', 'signed char', 'unsigned char'):
                self.value.value = char_to_string(self.v, printcfg.codepage)
                self.value.print_value()
            elif str(self.vtype) == 'wchar_t':
                self.value.value = str(self.v)
                self.value.print_value()
            elif self.vtype.code == gdb.TYPE_CODE_REF:
                self.target = self.ref()
                self.value.address = self.v.address
                self.value.print_value()
                self.target.print_v(name, depth, expr, pos, False, False, indent, mod)
                return
            elif self.vtype.code in (gdb.TYPE_CODE_ARRAY, gdb.TYPE_CODE_PTR):
                if self.vtype.code == gdb.TYPE_CODE_PTR:
                    self.value.address = longx(self.v)
                    if self.value.address == 0 or str(self.vtype) == "void *":
                        self.value.print_value()
                        self.value.print_post()
                        return
                    self.target = GdbValue(self.v.dereference())
                elif self.vtype.code == gdb.TYPE_CODE_ARRAY:
                    self.target = GdbValue(self.v[0])
                    self.value.address = self.v.address

                if str(self.target.vtype) in ('char', 'signed char', 'unsigned char'):
                    if mod.transform.v is None:
                        mod.transform.v = Transform.STR
                elif str(self.target.vtype) == 'wchar_t':
                    if mod.transform.v is None:
                        mod.transform.v = Transform.UNICODE
                elif self.vtype.code == gdb.TYPE_CODE_ARRAY and mod.transform.v is None:
                        mod.transform.v = Transform.ARRAY

                if self.vtype.code == gdb.TYPE_CODE_ARRAY:
                    self.size = self.vtype.sizeof / self.target.vtype.sizeof
                else:
                    self.size = -1

                if mod.transform.v == Transform.STR:
                    pos = mod.get_fetch(expr, pos, printcfg.fetch_string)
                    self.print_cstr(mod.ranges, mod.cp, indent)
                    return
                elif mod.transform.v == Transform.UNICODE:
                    pos = mod.get_fetch(expr, pos, printcfg.fetch_string)
                    self.print_unicode(mod.ranges, indent)
                    return
                elif mod.transform.v == Transform.ARRAY:
                    self.print_array(mod, depth, expr, pos, indent)
                    return
                else:
                    depth2 = mod.get_depth(expr, pos, depth)
                    #print_str("\n%d %d\n" %(depth, depth2))
                    #print_obj(self.value)
                    if depth2 >= 0:
                        self.value.subtype = SubType.PTR
                        self.value.print_value()
                        #self.value.print_space()
                        self.target.print_v(name, depth2, expr, pos, False, False, indent, mod)
                    else:
                        self.value.print_value(False, False, True)

            #end if self.vtype.code in (gdb.TYPE_CODE_ARRAY, gdb.TYPE_CODE_PTR)<F2>
            elif self.vtype.code == gdb.TYPE_CODE_ENUM:
                self.value.value = "%s (%d)" % (str(self.v), int(self.v))
                self.value.print_value()
            else:
                self.value.value = str(self.v)
                self.value.print_value()

            self.value.print_post()
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all()

    def print_cstr(self, ranges, cp, indent = ""):
        i = 0
        if len(ranges.range) > 1:
            self.value.subtype = SubType.MULTI

        cp_str = printcfg.codepage if cp is None else cp
        self.value.print_value()

        for r in ranges.range:
            (start, end) = calc_range(r[0], r[1], self.size)
            val_range = ValueOut()
            if start == -1:
                if i == 0:
                    val_range.range = "[]"
                    val_range.value = "None"
                    val_range.print_value()
                else:
                    continue 
            else:
                if start == end:
                    val_range.range = "[%d]" % start
                else:
                    val_range.range = "[%d:%d]" % (start, end)

                try: 
                    (s, l,  s_l) = read_string(self.v, start, end)
                    if printcfg.verbose > 1:
                        val_range.str_len = s_l
                    val_range.value = self.char_array_to_string(s, cp_str, False if s_l is None else True)

                except Exception as e:
                    val_range.error = error_format(e)
               
                if len(ranges.range) > 1:
                    val_range.print_pre(indent + printcfg.indent_pre)
                elif printcfg.verbose > 0:
                    val_range.print_space()

                val_range.print_value()

            i += 1
            if len(ranges.range) > 1:
                if i == len(ranges.range):
                    val_range.print_endline()
                else:
                    val_range.print_endline(True, True)

        self.value.print_post(indent)

    def char_array_to_string(self, char_array, cp, null_b = False):
        if cp is None:
            cp_str = printcfg.codepage
        else:
            cp_str = cp

        if null_b:
            null_end = " + \\0"
        else:
            null_end = ""
        try:
            result = ""
            s_decode = char_array.decode(cp_str)
            if cp_str in [ "utf-8" ] and len(s_decode) < len(char_array):
                result += cp_str + ":"
            result += '\"' + s_decode + '\"' + null_end
        except UnicodeDecodeError:
            result = printcfg.codepage_failback + ":"
            s_decode = char_array.decode(printcfg.codepage_failback)
            result += '\"' + s_decode + '\"' + null_end

        return result

    def print_unicode(self, ranges, indent = ""):
        i = 0
        if len(ranges.range) > 1:
            self.value.subtype = SubType.MULTI

        self.value.print_value()

        for r in ranges.range:
            (start, end) = calc_range(r[0], r[1], self.size)
            val_range = ValueOut()
            if start == -1:
                if i == 0:
                    val_range.range = "[]"
                    val_range.value = "None"
                    val_range.print_value()
                else:
                    continue 
            else:
                if start == end:
                    val_range.range = "[%d]" % start
                else:
                    val_range.range = "[%d:%d]" % (start, end)

                try: 
                    (s, l,  s_l) = read_unicode(self.v, start, end)
                    if printcfg.verbose > 1:
                        val_range.str_len = s_l

                    val_range.value = self.unicode_array_to_string(s, False if s_l is None else True)

                except Exception as e:
                    val_range.error = error_format(e)
                
                if len(ranges.range) > 1:
                    val_range.print_pre(indent + printcfg.indent_pre)
                elif printcfg.verbose > 0:
                    val_range.print_space()

                val_range.print_value()

            i += 1
            if len(ranges.range) > 1:
                if i == len(ranges.range):
                    self.value.print_endline()
                else:
                    self.value.print_endline(True, True)

        self.value.print_post(indent)

    def unicode_array_to_string(self, u_array, null_b = False):
        if null_b:
            null_end = " + \\0"
        else:
            null_end = ""
        
        result = 'L\"' + u_array + '\"' + null_end
        return result

    def print_kv(self, indent, n, k, v, depth, expr, pos):
        value = ValueOut("[%d]" % n)
        value.print_name(indent)
        try:
            kelem = GdbValue(k)
            ValueOut.print_prekv(True)
            kelem.print_v("key", 1, None, -1, False, True, indent + printcfg.indent_pre)
            ValueOut.print_postkv(True)

            velem = GdbValue(v)
            ValueOut.print_prekv()
            velem.print_v("value", depth, expr, pos, False, True, indent + printcfg.indent_pre)
            ValueOut.print_postkv()
            value.print_post("", True, True) 
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all("", True, True)
 
    def print_array_num_elem(self, velem, i, w, end, indent = "", char_type = 0, cp = None, uchar = None, cwidth = 0):
        vchar = ""
        value = ValueOut("[%d]" % i)
        if char_type == 1:
            if cp == "utf-8":
                c = char_unsign(velem.v)
                if c < 128:
                    vchar = ""
                    if len(uchar) > 0:
                        del uchar[:] 
                if len(uchar) == 1:
                    try:
                        uchar.append(c)
                        vchar = " " + cp + ":\"" + uchar.decode(cp) + "\""
                        del uchar[:] 
                    except:
                        del uchar[0]
                else:
                    uchar.append(c)
                    vchar = ""

            value.value = char_to_string(velem.v, cp) + vchar
            value.print_all(indent + printcfg.indent_pre, True, True)
        elif char_type == 2:
            value.value = str(velem.v)
            value.print_all(indent + printcfg.indent_pre, True, True)
        else:
            value.value = str(velem.v)
            if printcfg.out_type == OutType.TEXT and printcfg.width > 1 and cwidth > 0:
                s = value.name + " = " + value.value
                if len(s) >= cwidth:
                    s = value.name + " = " + value.value
                #cwidth = 6 + len(
                if w == 1:
                    print_str(indent + printcfg.indent_pre + s.ljust(cwidth) + ", ")
                    w += 1
                elif printcfg.width > w * cwidth:
                    print_str(s.ljust(cwidth) + ", ")
                    w += 1
                else:
                    print_str("%s,\n" % s.ljust(cwidth))
                    w = 1
            else:
                value.print_all(indent + printcfg.indent_pre, True, True)

        return w
            
    def print_array(self, mod, depth, expr, pos, indent = "", print_eq = True):
        #value = ValueOut()
        self.value.subtype = SubType.MULTI
        self.value.print_value()

        cp_str = printcfg.codepage if mod.cp is None else mod.cp

        pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
        pos = mod.get_filters(expr, pos)
        depth2 = mod.get_depth(expr, pos, depth)

        (num_type, cwidth) = calc_cwidth(self.target.vtype)
        
        uchar = None
        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], self.size)
            if start == -1:
                continue

            n = start
            if num_type == 1:
                if cp_str == "utf-8":
                    uchar = bytearray()
            try:
                w = 1
                if start <= end:
                    decr = 1
                else:
                    decr = -1
                while True:
                    if decr == 1:
                        if n > end:
                            break
                    elif decr == -1:
                        if n < end:
                            break
                    if self.vtype.code == gdb.TYPE_CODE_PTR:
                        elem = (self.v + n).dereference()
                    else:
                        elem = self.v[n]
                    velem = GdbValue(elem)
                    action = filters_check(velem, mod.filters)
                    if action == Filter.SKIP:
                        n += decr
                        continue
                    if num_type != -1:
                        w = self.print_array_num_elem(velem, n, w, end, indent, num_type, cp_str, uchar, cwidth)
                    else:
                        velem.print_v("[%d]" % n, depth2, expr, pos, True, True, indent + printcfg.indent_pre)
                        self.value.print_endline(True, True)

                    n += decr

                    if action == Filter.STOP:
                        break

                if w > 1:
                    self.value.print_endline()

            except Exception as e:
                value_err = ValueOut("[%d]" % n)
                if w > 1:
                    value_err.print_endline()
                value_err.error = error_format(e)
                value_err.print_all(indent + printcfg.indent_pre, True, True)

        self.value.print_post(indent)

    def print_struct(self, depth, expr, pos, indent, mod):
        if not mod.transform is None and mod.transform.v == Transform.SIMPLE:
            self.value.value = str(self.v)
            self.value.print_all(indent)
            return
        elif not mod.transform is None and mod.transform.v == Transform.RAW:
            obj = None
        elif self.vtype.code == gdb.TYPE_CODE_STRUCT:
            if not mod.transform is None and mod.transform.v == Transform.TYPE:
                obj = mod.transform.typeobj
            else:
                obj = resolve_printer(short_name(str(self.vtype)))
                if obj is None is None and mod.get_pos_type == FType.RANGE and not mod.ranges.next_v is None:
                    obj = resolve_printer_typename("list")
        else:
            obj = None
        if not obj is None:
            try:
                self.print_obj(obj, depth, expr, pos, indent, mod)
            except Exception as e:
                value_err = ValueOut()
                value_err.error = error_format(e)
                value_err.print_all(indent)
                return
        else: 
            self.print_fields(depth, expr, pos, indent, mod)

    def print_fields(self, depth, expr, pos, indent, mod):
        pos = mod.get_struct(expr, pos)
        fields = self.v.type.fields()
        depth2 = mod.get_depth(expr, pos, depth)
        self.value.subtype = SubType.MULTI
        self.value.print_value()
        i  = 0
        while i < len(fields):
            f = fields[i]
            i += 1
            depth3 = depth2
            if mod.sw is None:
                cast = None
            else:
                if f.name in mod.sw.hide_fields:
                    continue
                if f.name in mod.sw.noderef_fields:
                    depth3 = -1

                if len(mod.sw.fields) > 0 and not f.name in mod.sw.fields:
                    continue
                     
                cast = mod.sw.cast_fields.get(f.name)
            
            value_f = ValueOut(f.name)
            value_f.print_name(indent + printcfg.indent_pre)
            try:
                if cast is None:
                    felem = GdbValue(self.v[f.name])
                else:
                    felem = GdbValue(self.v[f.name]).cast(cast)

                felem.print_v(f.name, depth3, expr, pos, False, True, indent + printcfg.indent_pre)
            except Exception as e:
                s = str(e)
                if s.find("There is no member or method named") >= 0:
                    continue
                if s.find(" is nonexistent or has been optimized out") >= 0:
                    continue
                if s.find("cannot resolve overloaded method") >= 0:
                    continue
                value_f.error = error_format(e)
                value_f.print_all(indent + printcfg.indent_pre)

            value_f.print_post()
            if i == len(fields):
                value_f.print_endline()
            else:
                value_f.print_endline(True, True)

        self.value.print_post(indent)

    def print_obj(self, obj, depth, expr, pos, indent, mod):
        self.value.hint = obj.display_hint()
        if self.value.hint == DisplayType.STRING:
            self.print_obj_str(obj, expr, pos, indent, mod) 
        elif self.value.hint == DisplayType.ARRAY:
            self.print_obj_arr(obj, depth, expr, pos, indent, mod)
        elif self.value.hint in (DisplayType.LIST, DisplayType.LIST_SIZED):
            self.print_obj_list(obj, depth, expr, pos, indent, mod)
        elif self.value.hint == DisplayType.SET:
            self.print_obj_set(obj, depth, expr, pos, indent, mod)
        elif self.value.hint == DisplayType.BITSET:
            self.print_obj_bitset(obj, depth, expr, pos, indent, mod)
        elif self.value.hint == DisplayType.MAP:
            self.print_obj_map(obj, depth, expr, pos, indent, mod)
        elif self.value.hint == DisplayType.STRUCT:
            self.print_obj_struct(obj, depth, expr, pos, indent, mod)
        elif self.value.hint == DisplayType.SUBTYPE:
            mod.fields = obj.fields
            self.print_fields(depth, expr, pos, indent, mod)
        elif self.value.hint == DisplayType.PTR:
            p = obj(self.v, self.v.type)
            (ptr, desc) = p.ptr()
            if not desc is None:
                self.value.desc = desc
                #self.value.print_space()

            self.value.print_value()
            self.target = GdbValue(ptr)
            depth2 = mod.get_depth(expr, pos, depth)
            if depth2 >= 0:
                value = ValueOut()
                value.subtype = SubType.PTR
                if printcfg.verbose > 0: value.print_space()
                value.print_subtype()
                #value.print_space()
                self.target.print_v("ptr", depth2, expr, pos, False, True, indent, mod)
                value.print_post()
        else:
            raise ValueError("unsupported display type %d" % obj_hint)

    def print_obj_arr(self, obj, depth, expr, pos, indent, mod):
        try:
            pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
            pos = mod.get_filters(expr, pos)
            if mod.ranges is None:
                next_v = None
            else:
                next_v = mod.ranges.next_v

            ao = obj(self.v, self.v.type, next = next_v)
            (self.value.size, self.value.capacity) = ao.size()
            cp_str = printcfg.codepage if mod.cp is None else mod.cp
            depth2 = mod.get_depth(expr, pos, depth)
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        self.value.subtype = SubType.MULTI
        self.value.print_value()

        num_type = -1
        self.target = None
        uchar = None

        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], self.value.size)
            if start == -1:
                continue

            n = start
            w = 1

            if start <= end:
                decr = 1
            else:
                decr = -1
            while True:
                if decr == 1:
                    if n > end:
                        break
                elif decr == -1:
                    if n < end:
                        break

                try:
                    elem = ao.get(n)
                    velem = GdbValue(elem)
                    action = filters_check(velem, mod.filters)
                    if action == Filter.SKIP:
                        n += decr
                        continue

                    if self.target is None:
                        self.target = velem
                        (num_type, cwidth) = calc_cwidth(self.target.vtype)
                except Exception as e:
                    value_err = ValueOut("[%d]" % n)
                    value_err.error = error_format(e)
                    value.print_all(indent + printcfg.indent_pre, True)
                    break
            
                if num_type >= 0:
                    w = self.print_array_num_elem(velem, n, w, end, indent, num_type, cp_str, uchar, cwidth)
                else:
                    velem.print_v("[%d]" % n, depth2, expr, pos, True, True, indent + printcfg.indent_pre)
                    self.value.print_endline(True, True)

                n += decr
                if action == Filter.STOP:
                    break

            if w > 1:
                self.value.print_endline()
        
        self.value.print_post(indent)

    def print_obj_str(self, obj, expr, pos, indent, mod, print_eq = True):
        if mod.transform.v == Transform.ARRAY:
            default_fetch = printcfg.fetch_array
        else:
            default_fetch = printcfg.fetch_string

        try:
            pos = mod.get_fetch(expr, pos, default_fetch)
            pos = mod.get_filters(expr, pos)
            if mod.ranges is None:
                next_v = None
            else:
                next_v = mod.ranges.next_v

            cp_str = printcfg.codepage if mod.cp is None else mod.cp
            so = obj(self.v, self.v.type, next = next_v)
            (self.value.str_len, self.value.capacity) = so.size()
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        if mod.transform.v == Transform.ARRAY or len(mod.ranges.range) > 1:
            self.value.subtype = SubType.MULTI
        
        self.value.print_value()

        i = 0
        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], self.value.str_len)
            if start == -1:
                if mod.transform.v == Transform.ARRAY or i > 0:
                    continue

            if mod.transform.v == Transform.ARRAY:
                n = start
                uchar = bytearray() 
                w = 1
                if start <= end:
                    decr = 1
                else:
                    decr = -1
                while True:
                    if decr == 1:
                        if n > end:
                            break
                    elif decr == -1:
                        if n < end:
                            break

                    value_f = ValueOut("[%d]" % n)
                    try:
                        velem = GdbValue(so.get(n))
                        action = filters_check(velem, mod.filters)
                        if action == Filter.SKIP:
                            n += decr
                            continue

                        if so.is_unicode():
                            value_f.value = str(velem.v)
                        else:
                            c = char_unsign(velem.v)
                            vchar = ""
                            if cp_str == "utf-8":
                                if c < 128:
                                    if len(uchar) > 0:
                                        uchar = bytearray() 
                                if len(uchar) == 1:
                                    try:
                                        uchar.append(c)
                                        vchar = " " + cp_str + ":\"" + uchar.decode(cp_str) + "\""
                                        uchar = bytearray() 
                                    except:
                                        del uchar[0]
                                else:
                                    uchar.append(c)

                            value_f.value = char_to_string(c, cp_str) + vchar

                        value_f.print_all(indent + printcfg.indent_pre, True, True)

                        if action == Filter.STOP:
                            break
                        n += decr
                    except Exception as e:
                        value_f.error = error_format(e)
                        value_f.print_all(indent + printcfg.indent_pre, True, True)
                        w = 1
                        break

                    if w > 1:
                        value_f.print_endline()

            else:
                value_f = ValueOut()
                if start == -1:
                    value_f.range = "[]"
                else:
                    if start == end:
                        value_f.range = "[%d]" % start
                    else:
                        value_f.range = "[%d:%d]" % (start, end)
            
                    if start > end:
                        value_f.value = "None"
                    else:
                        (s, l,  s_l) = so.substring(start, end)
                        if so.is_unicode():
                            value_f.value = self.unicode_array_to_string(s, False)
                        else:
                            value_f.value = self.char_array_to_string(s, mod.cp, False)

                if len(mod.ranges.range) > 1:
                    value_f.print_pre(indent + printcfg.indent_pre)
                    value_f.print_all(indent + printcfg.indent_pre, True, True)
                else:
                    value_f.print_all(indent + printcfg.indent_pre)
    
            i += 1

        if len(mod.ranges.range) > 1 or mod.transform.v == Transform.ARRAY:
            self.value.print_post(indent)

    def print_obj_list(self, obj, depth, expr, pos, indent, mod):
        #print_obj(mod)
        try:
            pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
            pos = mod.get_filters(expr, pos)
            if mod.ranges is None:
                next_v = None
            else:
                next_v = mod.ranges.next_v
     
            lo = obj(self.v, self.v.type, next = next_v)
            if lo.display_hint() == DisplayType.LIST_SIZED:
                self.value.size = lo.size()

            depth2 = mod.get_depth(expr, pos, depth)
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        self.value.subtype = SubType.MULTI
        self.value.print_value()
        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], self.value.size)
            if start == -1 or start > end:
                continue
            
            if lo.get_pos() > start:
                lo.seek_first()

            while lo.get_pos() <= end:
                value_f = ValueOut("[%d]" % lo.get_pos())
                value_f.print_name(indent + printcfg.indent_pre)
                try:
                    (n,  elem) = lo.next()
                    if n < start:
                        continue

                    velem = GdbValue(elem)
                    action = filters_check(velem, mod.filters)
                    if action == Filter.SKIP:
                        continue

                    velem.print_v(value_f.name, depth2, expr, pos, False, True, indent + printcfg.indent_pre)
                    value_f.print_post("", True, True)
                except StopIteration:
                    value_f.address = 0
                    value_f.print_value()
                    value_f.print_post(indent + printcfg.indent_pre, True, True)
                    break
                except Exception as e:
                    value_f.error = error_format(e)
                    value_f.print_value()
                    value_f.print_post(indent + printcfg.indent_pre, True, True)
                    break

                n += 1
                if action == Filter.STOP:
                    break

        self.value.print_post(indent)

    def print_obj_set(self, obj, depth, expr, pos, indent, mod):
        try:
            pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
            if mod.ranges is None:
                next_v = None
            else:
                next_v = mod.ranges.next_v

            so = obj(self.v, self.v.type, next = next_v)
            self.value.size = so.size()

            depth2 = mod.get_depth(expr, pos, depth)
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        self.value.subtype = SubType.MULTI
        self.value.print_value()

        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], self.value.size)
            if start == -1 or start > end:
                continue
            
            if so.get_pos() > start:
                so.seek_first()

            while True:
                n = so.get_pos()
                if n > end:
                    break

                value_f = ValueOut("[%d]" % n)
                value_f.print_name(indent + printcfg.indent_pre)
                try:
                    elem = so.next()
                    if n < start:
                        continue

                    velem = GdbValue(elem)
                    velem.print_v(value_f.name, depth2, expr, pos, False, True, indent + printcfg.indent_pre)
                    value_f.print_post("", True, True)
                except StopIteration:
                    break
                except Exception as e:
                    value_f.error = error_format(e)
                    value_f.print_value()
                    value_f.print_post(indent + printcfg.indent_pre, True, True)
                    break

                n += 1

        self.value.print_post(indent)

    def print_obj_bitset(self, obj, depth, expr, pos, indent, mod):
        try:
            pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
            pos = mod.get_filters(expr, pos)
            bo = obj(self.v, self.v.type)
            depth2 = mod.get_depth(expr, pos, depth)
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        self.value.subtype = SubType.MULTI
        self.value.print_value()

        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], -1)
            if start == -1 or start > end:
                continue
            e = None
            try:
                e = bo.get(start, end)
            except StopIteration:
                continue
            except Exception as e:
                value_err = ValueOut("[]")
                value_err.error = error_format(e)
                value_err.print_all(indent + printcfg.indent_pre, True, True)
                continue
            
            #print_str(str(e))
            for v in e[0]:
                velem = GdbValue(gdb.Value(v[1]))
                action = filters_check(velem, mod.filters)
                if action == Filter.SKIP:
                    continue

                value_f = ValueOut("[%d]" % v[0])
                value_f.value = str(v[1])
                value_f.print_all(indent + printcfg.indent_pre, True, True)

                if action == Filter.STOP:
                    break

        self.value.print_post(indent)

    def print_obj_map(self, obj, depth, expr, pos, indent, mod):
        try:
            pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
            pos = mod.get_filters(expr, pos)
            if mod.ranges is None:
                next_v = None
            else:
                next_v  = mod.ranges.next_v

            so = obj(self.v, self.v.type, next = next_v)
            self.value.size = so.size()
            depth2 = mod.get_depth(expr, pos, depth)
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        self.value.subtype = SubType.MULTI
        self.value.print_value()

        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], self.value.size)
            if start == -1 or start > end:
                continue
            
            if so.get_pos() > start:
                so.seek_first()

            while True:
                n = so.get_pos()
                if n > end:
                    break
                try:
                    (k, v) = so.next()
                    if n < start:
                        continue

                    self.print_kv(indent + printcfg.indent_pre, n, k, v, depth2, expr, pos)
                except StopIteration:
                    break
                except Exception as e:
                    value_err = ValueOut("[%d]" % n)
                    value_err.error = error_format(e)
                    value_err.print_all(indent + printcfg.indent_pre, True, True)
                    break

        self.value.print_post(indent)

    def print_obj_struct(self, obj, depth, expr, pos, indent, mod, print_eq = True):
        try:
            pos = mod.get_fetch(expr, pos, printcfg.fetch_array)
            pos = mod.get_filters(expr, pos)
            if mod.ranges is None:
                next_v = None
            else:
                next_v  = mod.ranges.next_v

            lo = obj(self.v, self.v.type, next = next_v)
            depth2 = mod.get_depth(expr, pos, depth)
        except Exception as e:
            value_err = ValueOut()
            value_err.error = error_format(e)
            value_err.print_all(indent)
            return

        self.value.subtype = SubType.MULTI
        self.value.print_value()

        for r in mod.ranges.range:
            (start, end) = calc_range(r[0], r[1], -1)
            if start == -1 or start > end:
                continue
          
            while True:
                try:
                    (n,  v) = lo.next()
                    if n < start:
                        continue
                    elif n > end:
                        break
                except StopIteration:
                    break

                value_f = ValueOut("[%d]" % n)
                value_f.print_name(indent + printcfg.indent_pre)
                try:
                    velem = GdbValue(v)
                    action = filters_check(velem, mod.filters)
                    if action == Filter.SKIP:
                        continue
 
                    velem.print_v("[%d]" % n, depth2, expr, pos, False, True, indent + printcfg.indent_pre)
                except Exception as e:
                    value_f.error = error_format(e)
                    value_f.print_value()

                value_f.print_post("", True, True)

                n += 1
                if action == Filter.STOP:
                    break

        self.value.print_post(indent)


class GdbVisitor:
    def eval(self, v):
        return GdbValue(gdb.parse_and_eval(v))

    def from_addr(self, v):
        return GdbValue(gdb.Value(v))

    def init(self, s):
        v = GdbValue(s)
        return v

    def oper(self, flist, op):
        for f in flist:
            if f.t == FType.VAL:
                if not gdbutils.is_iter_typecode(f.vtype.code):
                    raise ValueError("not supported operator for %s" % gdbutils.typename(f.vtype.code))
                elif f.v.is_optimized_out:
                    raise ValueError("not supported operator for optimized %s %s" % (str(f.vtype), str(f.v)))

        if op.t == FType.SUM:
            v = flist[0].v + flist[1].v
        elif op.t == FType.MINUS:
            v = flist[0].v - flist[1].v
        elif op.t == FType.MUL:
            v = flist[0].v * flist[1].v
        elif op.t == FType.DIV:
            v = flist[0].v / flist[1].v
        else:
            raise ValueError("non supported operator %s for %s" % (str(op), str(self)))
        return GdbValue(v)

    def deref(self, p):
        return GdbValue(p.v.dereference())

    def ref(self, r):
        return GdbValue(r.v.referenced_value())

    def list_locals(self):
        frame = gdb.selected_frame()
        frame_func  = None
        try:
            block = frame.block()
            frame_func = str(frame.function())
            #warn('BLOCK: %s ' % block)
        except RuntimeError as error:
            #warn('BLOCK IN FRAME NOT ACCESSIBLE: %s' % error)
            return []
        except:
            print_debug('BLOCK NOT ACCESSIBLE FOR UNKNOWN REASONS')
            return []

        items = []

        if block is None:
            print_debug("UNEXPECTED 'None' BLOCK")
            return []

        while block:
            if block.is_global:
                break
            for symbol in block:

              # Filter out labels etc.
                if symbol.is_variable or symbol.is_argument:
                    if symbol.print_name in ('__in_chrg', '__PRETTY_FUNCTION__',  'std::__ioinit'):
                        continue

                    # 'NotImplementedError: Symbol type not yet supported in
                    # Python scripts.'
                    try:
                        value = frame.read_var(symbol, block)
                        items.append((frame_func, symbol.print_name, value))
                    except:
                        print_debug(symbol.print_name + " " + traceback.format_exc(8))

            block = block.superblock

        return items

    def list_globals(self):
        frame = gdb.selected_frame()

        try:
            block = frame.block()
            #warn('BLOCK: %s ' % block)
        except RuntimeError as error:
            #warn('BLOCK IN FRAME NOT ACCESSIBLE: %s' % error)
            return []
        except:
            print_debug('BLOCK NOT ACCESSIBLE FOR UNKNOWN REASONS')
            return []

        items = []
        #shadowed = {}

        if block is None:
            print_debug("UNEXPECTED 'None' BLOCK")
            return

        while block:
            if block.is_global:
                for symbol in block:

                  # Filter out labels etc.
                  if symbol.is_variable or symbol.is_argument:
                    if symbol.print_name in ('__in_chrg', '__PRETTY_FUNCTION__'):
                        continue

                    try:
                        value = frame.read_var(symbol, block)
                        items.append((None, symbol.print_name, value))
                    except:
                        print_debug(symbol.print_name + " " + traceback.format_exc(8))

            block = block.superblock

        return items

    def print_frame(self, is_global, depth = None):
        if depth is None:
            depth = printcfg.depth
        if is_global:
            values = self.list_globals()
        else:
            values = self.list_locals()
        l = len(values)
        if values is None or l == 0:
            return
        values.sort(key=lambda tup: tup[1])
        if is_global:
            ValueOut.print_section("global")
        else:
            ValueOut.print_section(values[0][0])
        for v in values:
            value = ValueOut(v[1])
            value.print_name(printcfg.indent_pre)
            try:
		#print_str(str(v) + "\n")
                gv = GdbValue(v[2])
                gv.print_v(value.name, depth, None, -1, False, True, printcfg.indent_pre)
                value.print_endline(True, True)
            except Exception as e:
                value.error = error_format(e)
                value.print_value(True, True)

        ValueOut.print_section_end()

