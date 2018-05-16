import sys
import shlex
import re

import traceback
#from value import Value, CastType

from collections import deque

from . import printcfg
from .printcfg import OutType
from .define import longx
from .gdbutils import print_str
from .utils import print_debug, print_warn, print_error, print_obj
from .utils import error_format
from .utils import resolve_printer_typename

#import pprint

#from collections import defaultdict

def tree_str(t):
    return " ".join(str(x) for x in t)


# Check Filter's list against DebuggerValue (GdbValue, etc)
def filters_check(v, filters):
    if filters is None:
        return Filter.PASS
    else:
        action = Filter.PASS
        for f in filters:
            action = v.check(f)
            if action != Filter.PASS:
                return action
        return action

def calc_range(r0, r1, size, visitor = None):
    #print_str(str(r0) + " " + str(r1) + " " + str(size) + "\n")
    if r0.t == FType.NUM:
        start = r0.v
    elif visitor is None or r0.t != FType.EXPR:
        raise ValueError("%s is not supported as range start" % str(r2))
    else:
        try:
            v = r0.eval(visitor)
            start = v[0].num()
        except:
            raise ValueError("%s is not a number at range start" % str(r0))

    if r1.t == FType.NUM:
        end = r1.v
    elif visitor is None or r1.t != FType.EXPR:
        raise ValueError("%s is not supported as range end" % str(r1))
    else:
        try:
            v = r1.eval(visitor)
            end = v[0].num()
        except:
            raise ValueError("%s is not a number at range end" % str(r1))

    if size == -1 or size is None:
        return (start, end)
    elif size == 0:
        return (-1, -1)
    else:
        if start > size - 1:
            if end > size -1:
                return (-1, -1)
            else:
                start = size - 1
        if end > size - 1:
            end = size - 1
        return (start, end)


class Mod:
    def __init__(self, transform = None, cp = None, filters = None, ranges = None, sw = None):
        self.transform = transform
        self.cp = None
        self.filters = filters
        self.ranges = ranges
        self.sw = sw

    def get_depth(self, expr, pos, depth):
        #print_debug("\n%d %d %d\n" % (pos, depth, len(expr.v)))
        if depth == -1:
            return -1
        elif pos == -1 or pos >= len(expr.v):
            return depth - 1
        return depth

    def get_pos_type(self, expr, pos):
        if expr is None or pos == -1 or pos >= len(expr.v):
            return None
        else:
            return expr.v[pos].t

    def get_struct(self, expr, pos):
        if expr is None or pos == -1 or pos >= len(expr.v) or expr.v[pos].t != FType.STRUCT:
            self.sw = None
            return pos
        else:
            self.sw = expr.v[pos]
            return pos + 1

    def get_transform(self, expr, pos, t = None):
        if expr is None or pos == - 1 or pos >= len(expr.v):
            self.transform = Transform()
            return -1
        elif expr.v[pos].t != FType.TRANSFORM:
            #print_obj(expr.v[pos])
            if t is None:
                self.transform = Transform()
            else:
                self.transform = t
            self.cp = None
            return pos
        else:
            #print_obj(expr.v[pos])
            self.transform = expr.v[pos]
            if expr.v[pos].cp is None:
                self.cp = printcfg.codepage
            else:
                self.cp = Transform.code_page[expr.v[pos].cp]
            #print_obj(self)
            return pos + 1

    def get_fetch(self, expr, pos, default_fetch):
        if expr is None or pos == -1 or pos >= len(expr.v):
            start = 0
            self.ranges = Range(start, start + default_fetch - 1)
            return pos
        elif expr.v[pos].t != FType.RANGE:
            raise ValueError("%s not a range" % str(expr.v[pos]))
        elif len(expr.v[pos].range) == 0:
            self.ranges = Range(0, default_fetch - 1, expr.v[pos].next_v)
            return pos + 1
        else:
            self.ranges = expr.v[pos]
            return pos + 1

    def get_filters(self, expr, pos):
        if expr is None or pos == -1 or pos >= len(expr.v) or expr.v[pos].t != FType.FILTER:
            self.filters = None
            return pos
        else:
            self.filters = list()
            while pos < len(expr.v):
                if expr.v[pos].t == FType.FILTER:
                    self.filters.append(expr.v[pos])
                    pos += 1
                else:
                    break
            return pos

class SubType:
    NONE = 0
    MULTI = 1
    PTR = 2

class ValueOut:
    def __init__(self, name = None, value = None, typename = None):
        self.name = name
        self.typename = typename
        self.address = value
        #self.key = None
        self.value = None
        self.error = None
        self.range = None
        self.str_len = -1
        self.size = -1
        self.capacity = -1
        self.subtype = None
        self.desc = None

    def print_str(self, s):
        print_str(s)

    def print_space(self):
        self.print_str(" ")

    def print_pre(self, indent):
        print_str(indent)

    def print_name(self, indent = "", space = True):
        if not self.name is None:
            if printcfg.out_type == OutType.TEXT and self.name[0] == "[" and self.name[-1] == "]":
                name = self.name
            else:
                name = "\"%s\"" % self.name
            if printcfg.out_type == OutType.NAMED:
                self.print_str("%s{ name = %s," % (indent, name))
            else:
                self.print_str("%s%s =" % (indent, name))

        if space: self.print_space()

    def print_value(self, endline = False, comma = False, p_addr = False):
        #print_obj(self)
        out = list()
        if not self.typename is None and printcfg.verbose > 0:
            if printcfg.out_type == OutType.NAMED:
                out.append("type = \"%s\"," % self.typename)
            else:
                out.append("(%s)" % self.typename)

        if not self.address is None:
            if self.address == 0 or printcfg.verbose > 0 or p_addr or self.typename == "void *":
                addr = "<0x%x>" % self.address
                if printcfg.out_type == OutType.NAMED:
                    out.append("addr = %s," % addr)
                else:
                    out.append(addr)

            if self.address == 0:
                self.print_str(" ".join(out))
                return


        if not self.desc is None and printcfg.verbose > 1:
            if printcfg.out_type == OutType.NAMED:
                out.append("desc = \"%s\"," % self.desc)
            else:
                out.append("desc:\"%s\"" % self.desc)
 
        len_str = ""
        if printcfg.verbose > 1:
            if not self.str_len is None and self.str_len != -1:
                if printcfg.out_type == OutType.NAMED:
                    len_str += " str_len = %d," % self.str_len
                else:
                    len_str += " str_len:%d" % self.str_len

            if not self.size is None and self.size != -1:
                if printcfg.out_type == OutType.NAMED:
                    len_str += " size = %d," % self.size
                else:
                    len_str += " size:%d" % self.size

            if not self.capacity is None and self.capacity != -1:
                if printcfg.out_type == OutType.NAMED:
                    len_str += " capacity = %d," % self.capacity
                else:
                    len_str += " capacity:%d" % self.capacity

       
        if self.error is None and not self.subtype is None:
            if len(len_str) > 0:
                out.append(len_str[1:])
            if len(out) > 0: self.print_str(" ".join(out))
            self.print_subtype(False if printcfg.verbose == 0 else True) 
            return

        if not self.range is None:
            if printcfg.out_type == OutType.NAMED:
                out.append("range = {%s name = \"%s\"," % (len_str, self.range))
            else:
                out.append("{%s %s =" % (len_str, self.range))
        elif len(len_str) > 0:
            out.append(len_str[1:])

        if not self.error is None:
            if printcfg.out_type == OutType.NAMED:
                out.append("error = \"%s\"" % self.error)
            else:
                out.append("error:\"%s\"" % self.error)
        elif not self.value is None:
            if printcfg.out_type == OutType.NAMED:
                v = self.value.replace("\"", "\\\"")
                out.append("value = \"%s\"" % v)
            else:
                out.append(self.value)
        elif not self.range is None:
            if printcfg.out_type == OutType.NAMED:
                out.append("value = None")
            else:
                out.append("None")
 
        if not self.range is None:
            out.append("}")

        self.print_str(" ".join(out))
        self.print_endline(endline, comma)

    def print_endline(self, endline = True, comma = False):
        addstr = ""
        if comma:
            addstr += ","
        if endline:
            addstr += "\n"

        if endline or comma:
            print_str(addstr)


    def print_subtype(self, space = False):
        if self.error is None and not self.subtype is None:
            if space: self.print_space()
            if self.subtype == SubType.MULTI:
                if printcfg.out_type == OutType.NAMED:
                    self.print_str("value = {\n")
                else:
                    self.print_str("{\n")
            elif self.subtype == SubType.PTR:
                if printcfg.out_type == OutType.NAMED:
                    self.print_str("ptr = { ")
                else:
                    self.print_str("{ ptr = ")

    def print_post(self, indent = "", endline = False, comma = False, end = False):
        if self.subtype == SubType.MULTI and self.error is None:
            print_str("%s}" % indent)
        elif self.subtype == SubType.PTR and self.error is None:
            print_str(" }")

        if (end or not self.name is None) and printcfg.out_type == OutType.NAMED:
            print_str(" }")

        self.print_endline(endline, comma)

    def print_all(self, indent = "", endline = False, comma = False):
        self.print_name(indent, True)
        self.print_value()
        self.print_post(indent, endline, comma)

    @staticmethod
    def print_prekv(key = False):
        if printcfg.out_type == OutType.NAMED:
            s = "key" if key else "value"
            print_str("%s = { " % s)
        else:
            print_str("{ ")

    @staticmethod
    def print_postkv(key = False):
        if printcfg.out_type == OutType.NAMED:
            print_str(" }, ")
        elif key:
            print_str(" } => ")
        else:
            print_str(" }")

    @staticmethod
    def print_section(s, indent = ""):
        if printcfg.out_type == OutType.NAMED:
            print_str("%sframe = \"%s\", values = {\n" % (indent, s))
        else:
            print_str("%sframe = \"%s\" {\n" % (indent, s))

    @staticmethod
    def print_section_end(indent = ""):
            print_str("%s}\n" % indent)


class OperLoc:
    NONE = 0 # No Location
    LEFT = 1 # One field
    CENTR = 2 # 2 filed
    #RIGHT = 3 # Not used now


class FType:
    NONE = 0
    EXPR = 1 # Expression
    THIS = 2 # In filter - current variable

    NAME = 3 # Name - expand with debugger API
    r_NAME = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    VAL = 4 # Expanded value from debugger

    ERR = 5 # Debugger error

    NUM = 10 # Integer number
    r_NUM = re.compile(r'^-?\d+$')

    FLOAT = 11 # Float number
    #r_FLOAT = re.compile(r'^-?\d+(.\d+)?$')
    r_FLOAT = re.compile(r'^-?\d+(.\d+)?(e-?\d+)?$')

    ADDR = 12
    r_ADDR = re.compile(r'^(0x[0-9a-fA-F]+)$')

    STR = 13

    RANGE = 20 # Range
    FILTER = 21 # Filer
    STRUCT = 22 # Filter structure fields
    TRANSFORM = 23 # Transfor array (arr, str, utf-8 str, simple, raw)

    DEREF = 31 # Dereference
    REF = 32 # Reference
    CAST = 33 # Cast

    NEG = 40 # - A
    SUM = 41 # A + B
    MINUS = 42  # A - B
    MUL = 43 # A * B
    DIV = 44 # A / B

    def __init__(self, s, t = None, name = None):
        if t is None:
            self.t = FType.NONE
            self.v = None
            #if self.t_NUM(s) or self.t_FLOAT(s) or self.t_NAME(s):
            if self.t_NUM(s) or self.t_FLOAT(s) or self.t_NAME(s) or self.t_ADDR(s):
                return
            else:
                raise ValueError("field format error: %s" % s)
        else:
            self.t = t
            self.v = s

        self.name = name

    def t_NUM(self, s):
        if FType.r_NUM.match(s) is None:
            return False
        else:
            self.v = longx(s)
            self.t = FType.NUM
            return True

    def t_FLOAT(self, s):
        if FType.r_FLOAT.match(s) is None:
            return False
        else:
            self.v = float(s)
            self.t = FType.FLOAT
            #self.name = "%e" % self.v
            return True

    def t_NAME(self, s):
        if FType.r_NAME.match(s) is None:
            return False
        else:
            self.v = s
            self.t = FType.NAME
            return True

    def t_ADDR(self, s):
        if FType.r_ADDR.match(s) is None:
            return False
        else:
            self.v = longx(s, 16)
            self.t = FType.ADDR
            return True

    def __str__(self):
        if self.t == FType.NAME:
            return "NAME(%s)" % self.v
        elif self.t == FType.NUM:
            return "NUM(%d)" % self.v
        elif self.t == FType.FLOAT:
            return "FLOAT(%e)" % self.v
        elif self.t == FType.CAST:
            return "CAST(%s)" % self.v
        elif self.t == FType.THIS:
            return "_";
        #elif self.t == FType.FLOAT:
        #    return "FLOAT(%f)" % self.v
        else:
            return str(self.v)

    def print_v(self, name, depth, expr, pos, print_name = True):
        value = ValueOut(name)
        #if not name is None and print_name:
        #    print_str("\"" + name + "\" =")
        
        if self.t == FType.ERR:
            #print_str(" %s" % self.v)
            value.error = self.v
        else:
            if pos < len(expr.v):
                raise ValueError("no ranges, filters and etc for simple type") 
            if self.t in (FType.NUM, FType.FLOAT):
                #print_str(" %s" % str(self.v))
                value.value = str(self.v)
            else:
                raise ValueError("%s (%d) need to be eval" % (str(self), self.t))

        value.print_value()
        value.print_post()


    def eval(self, visitor = None):
        if self.t == FType.NAME:
            if visitor is None:
                raise ValueError("no visitor set for type %d" % self.t)
            return (visitor.eval(self.v), 0)
        elif self.t == FType.ADDR:
            if visitor is None:
                raise ValueError("no visitor set for type %d" % self.t)
            return (visitor.from_addr(self.v), 0)
        elif self.t in (FType.NUM, FType.FLOAT):
            return (self, 0)
        else:
            raise ValueError("no eval method for type %d" % self.t)


class Expr:
    def __init__(self, s):
        self.t = FType.EXPR
        self.v = s
        #print_obj(self.v)

    def __str__(self):
        return "(%s)" % tree_str(self.v)

    def eval(self, visitor = None):
        #print(str(self))
        if self.v is None or len(self.v) == 0:
            return (FType(0, FType.NUM), 0)

        pos = 0
        #spos = 0
        flist = []
        while pos < len(self.v):
            if self.v[pos].t in [ FType.NUM, FType.FLOAT, FType.NAME, FType.EXPR ]:
                v = self.v[pos].eval(visitor)
                flist.append(v[0])
            elif self.v[pos].t in [ FType.NEG, FType.SUM, FType.MINUS, FType.DIV, FType.MUL ]:
                v = self.v[pos].eval(flist, visitor)
                #if printcfg.debug:
                #    print_obj(v[0])
                del flist[:]
                flist.append(v[0])
            elif self.v[pos].t == FType.DEREF:
                #raise ValueError("not supported deref")
                v = flist[-1].deref()
                flist[-1] = v
            elif self.v[pos].t == FType.REF:
                #raise ValueError("not supported ref")
                v = flist[-1].ref()
                flist[-1] = v
            elif self.v[pos].t == FType.CAST:
                #print_obj(flist)
                #print_obj(self.v[pos])
                #raise ValueError("not supported cast")
                v = flist[-1].cast(self.v[pos].v)
                flist[-1] = v
            elif self.v[pos].t == FType.ADDR:
                v = self.v[pos].eval(visitor)
                flist.append(v[0])
            elif self.v[pos].t in [ FType.RANGE, FType.STRUCT, FType.FILTER, FType.TRANSFORM ]:
                break
            else:
                raise ValueError("unsupported value " + str(self.v[pos]))

            pos += 1
           
        if len(flist) == 1:
            return (flist[0], pos)
        else:
            raise ValueError("incorrect expression: %s elements at the end" % len(flist))

    def eval_print(self, visitor = None, name = None, depth = None):
        if depth is None:
            depth = printcfg.depth
        value = ValueOut(name)
        value.print_name()
        try:
            v = self.eval(visitor)
            v[0].print_v(name, depth, self, v[1], False)
            value.print_post("", True)
        except Exception as e:
            value.error = error_format(e)
            value.print_value()
            value.print_post("", True)
            return


class Range:
    t = FType.RANGE

    def init(self):
        self.next_v = None 
        self.range = list()

    def __init__(self, a1, a2 = None, next_v = None):
        self.init()
        if a2 is None and next_v is None:
            #print_str(str(a1) + "\n")
            self.init_str(a1)
        else:
            if a1 is None:
                a1 = 0
            if a2 is None:
                a2 = 0
            self.range.append((self.r(a1), self.r(a2)))
            self.next_v = next_v

    def init_str(self, s):
        i = s.split("-->", 2)
        if len(i) > 2:
            raise ValueError("multiple -->")
        elif len(i) == 2:
            self.next_v = i[1]
            #print(i[1])
    
        if i[0] == "":
            return

        for r in i[0].split(","):
            ri = r.split(":", 2)
            if len(ri) > 2:
                raise ValueError("multiple :")
            elif len(ri) == 2:
                if ri[1] == '':
                    raise ValueError("range incorrect: %s" % str(s))
                if ri[0] == '':
                    r1 = self.r(0)
                else:
                    r1 = self.r(ri[0])
                r2 = self.r(ri[1])
                self.range.append((r1, r2))
            else:
                r1 = self.r(ri[0])
                self.range.append((r1, r1))

    def r(self, s):
        try:
            return FType(longx(s), FType.NUM)
        except ValueError:
            try:
                cmd_parse = CommandParser()
                return Expr(cmd_parse.parse1(s))
            except:
                raise ValueError("range format error: '%s' is not valid" % str(s))

    def str_r(self, r):
        if r.t == FType.NUM:
            return str(r.v)
        else:
            return str(r)

    def __str__(self):
        s = "[ "
        first = True
        for r in self.range:
            if first:
                first = False
            else:
                s += ", "

            if r[0] == r[1]:
                s += self.str_r(r[0])
            else:
                s += "%s:%s" % (self.str_r(r[0]), self.str_r(r[1]))

        if not self.next_v is None:
            s += " --> %s" % self.next_v

        s += " ]"
        return s


class Transform:
    t = FType.TRANSFORM

    ARRAY = 0
    RAW = 1
    SIMPLE = 2
    TYPE = 3

    UNICODE = 8
    STR = 9
    UTF8 = 10

    code_page = {
        UTF8 : "utf-8",
    }

    def __init__(self, s = None):
        self.v = None
        self.cp = None
        if s is None or s == "":
            return
        sp = s.split(",")
        if len(sp) > 2:
            raise ValueError("too many fields in '%s'" % s)
        for s1 in sp: 
            s2 = s1.lower().strip()
            if s2 in ("a", "arr", "array"):
                if not self.v is None:
                    raise ValueError("incompatible transform options: %s" %s)
                self.v = Transform.ARRAY
            elif s2 in ("s", "str", "string"):
                if not self.v is None:
                    raise ValueError("incompatible transform options: %s" %s)
                self.v = Transform.STR
            elif s2 in ("u8", "utf8", "utf-8"):
                self.cp = Transform.UTF8
            elif s2 in ("r", "raw"):
                self.v = Transform.RAW
            elif s2 == "simple":
                self.v = Transform.SIMPLE
            else:
                #i = s2.find("=")
                #if i == -1:
                    self.typeobj = resolve_printer_typename(s2)
                    if self.typeobj is None:
                        raise ValueError("unsupported transform '%s'" % s)
                    self.typename = s2
                    self.v = Transform.TYPE
                #else:


    def __str__(self):
        t = list()
        for v in (self.v, self.cp):
            if v is None:
                continue
            elif v == Transform.ARRAY:
                t.append("array")
            elif v == Transform.STR:
                t.append("str")
            elif v == Transform.UTF8:
                t.append("utf-8")
            elif v == Transform.TYPE:
                t.append(self.typename)
            elif v == Transform.RAW:
                t.append("raw")
            elif v == Transform.SIMPLE:
                t.append("simple")
            else:
                t.append("unknown (%d)" % v)
            s = "<%s>" % ",".join(t)
        return s



class CmpVal:
    EQ = 0
    EQ_S = "="
    NE = 1
    NE_S = "!="
    GT = 2
    GT_S = ">"
    GE = 3
    GE_S = ">="
    LT = 4
    LT_S = "<"
    LE = 5
    LE_T = "<="


    @staticmethod
    def cmpval(t):
        if t == CmpVal.EQ_S:
            return CmpVal.EQ
        elif t == CmpVal.NE_S:
            return CmpVal.NE
        elif t == CmpVal.GT_S:
            return CmpVal.GT
        elif t == CmpVal.GE_S:
            return CmpVal.GE
        elif t == CmpVal.LT_S:
            return CmpVal.LT
        elif t == CmpVal.LE_S:
            return CmpVal.LE
        else:
            raise ValueError("unknown compare %s" %s)

    @staticmethod
    def str(t):
        if t == CmpVal.EQ:
            return CmpVal.EQ_S
        elif t == CmpVal.NE:
            return CmpVal.NE_S
        elif t == CmpVal.GT:
            return CmpVal.GT_S
        elif t == CmpVal.GE:
            return CmpVal.GE_S
        elif t == CmpVal.LT:
            return CmpVal.LT_S
        elif t == CmpVal.LE:
            return CmpVal.LE_S
        else:
            return str(t)


class FilterItem:
    r_CMP = re.compile(r'^([A-Za-z_0-9]+)([=!<>]+)([A-Za-z_0-9]+)$')

    def __init__(self, s):
                
        self.c1 = None
        self.cmp_v = None
        self.c2 = None

        if FType.r_NUM.match(s):
            #self.stop_v = int(ci_s)
            self.c1 = FType("_", FType.THIS)
            self.c2 = FType(s)
            self.cmp_v = CmpVal.EQ;
        else:
            ci = FilterItem.r_CMP.match(s)
            if ci is None:
                raise ValueError("invalid filter '%s' items count" % s)
            self.cmp_v = CmpVal.cmpval(ci.group(2))
            
            if ci.group(1) == "_":
                self.c1 = FType("_", FType.THIS)
            else:
                self.c1 = FType(ci.group(1))
                if not self.c1.t == FType.NAME:
                    raise ValueError("invalid filter '%s' first item" % s)
            if ci.group(3) == "_":
                raise ValueError("invalid filter '%s' second item" % s)
            else:
                self.c2 = FType(ci.group(3))
                if not self.c2.t in (FType.NAME, FType.NUM):
                    raise ValueError("invalid filter '%s' second item" % s)

            if self.c1.t == self.c2.t and self.c1.v == self.c2.v:
                raise ValueError("invalid filter '%s' equal items" % s)
            elif self.c1.t == FType.THIS and self.c2.t != FType.NUM:
                raise ValueError("invalid filter '%s' items combination" % s)

    def __str__(self):
        return "%s %s %s" % (self.c1, CmpVal.str(self.cmp_v), self.c2)


class Filter:
    t = FType.FILTER

    #Actions
    PASS = 0
    SKIP = 1
    STOP = 2

    def __init__(self, s):
        self.fi = list()
        if s[0] == "@":
            self.stopkey = True
            #self.stop_v = None
            sp = s[1:]
        else:
            self.stopkey = False
            #self.stop_v = None
            sp = s

        for si in sp.split('||'):
            self.fi.append(FilterItem(si))

    def __str__(self):
        if self.stopkey:
            s = "{ @ "
        else:
            s = "{ "
        s += " || ".join(str(x) for x in self.fi)
        s += " }"
        return s
            

class Oper:
    set_visited = frozenset([ FType.DEREF, FType.REF, FType.CAST ])

    set_name = frozenset([ FType.NAME ])
    set_ariphmetic = frozenset([ FType.NAME, FType.NUM, FType.FLOAT ])

    sel_all = set_ariphmetic 

# t Oper Type
# s Oper Name
# prio Oper Priority
# loc Oper Location
# allow_multi Alloow seuence equivalent operators 
    def __init__(self, t = FType.NONE):
        if t is None or t == FType.NONE:
            self.__init(FType.NONE, None, 0, False, OperLoc.NONE)
        elif t == FType.CAST:
            self.__init(t, "CAST", 9, False, OperLoc.LEFT)
        elif t == FType.DEREF:
            self.__init(t, "DEREF", 10, True, OperLoc.LEFT)
        elif t == FType.REF:
            self.__init(t, "REF", 10, True, OperLoc.LEFT)
        elif t == FType.NEG:
            self.__init(t, "NEG", 0, False, OperLoc.LEFT)
        elif t == FType.MUL:
            self.__init(t, "*", 5, False, OperLoc.CENTR)
        elif t == FType.DIV:
            self.__init(t, "/", 5, False, OperLoc.CENTR)
        elif t == FType.SUM:
            self.__init(t, "+", 0, False, OperLoc.CENTR)
        elif t == FType.MINUS:
            self.__init(t, "-", 0, False, OperLoc.CENTR)
        else:
            raise ValueError("unhandled operation %s (%d)" % (s, t))

    def __init(self, t, s, pri, allow_multi, loc):
        if t == FType.NONE:
            self.allow_types = set_all
        elif t in (FType.DEREF, FType.REF):
            self.allow_types = Oper.set_name
        elif t in (FType.NEG, FType.SUM, FType.MINUS, FType.MUL, FType.DIV):
            self.allow_types = Oper.set_ariphmetic
        
        self.t = t
        self.s = s
        self.pri = pri
        self.allow_multi = allow_multi
        self.loc = loc

    def __str__(self):
        if self.t == FType.NONE:
            return ""
        elif self.t == FType.CAST:
            return "CAST(" + self.s + ")"
        else:
            return self.s

    def eval(self, flist, visitor):
        if self.t in (FType.SUM, FType.MINUS, FType.MUL, FType.DIV):
            if len(flist) == 2:
                if not flist[0].t in (FType.NUM, FType.FLOAT, FType.VAL):
                    raise ValueError("not supported argument %s for %s" % (str(flist[0]), str(self)))
                elif flist[0].t == flist[1].t:
                    t = flist[0].t
                elif flist[1].t == FType.NUM:
                    t = flist[0].t
                elif flist[1].t == FType.VAL:
                    t = FType.VAL
                elif flist[0].t == FType.FLOAT and flist[1].t == FType.NUM:
                    t = FType.FLOAT
                else:
                    raise ValueError("not supported combination of arguments %s and %s for %s" % (str(flist[0]), str(flist[1]), str(self)))

                if t in (FType.NUM, FType.FLOAT):
                    if self.t == FType.SUM:
                        v = flist[0].v + flist[1].v
                    elif self.t == FType.MINUS:
                        v = flist[0].v - flist[1].v
                    elif self.t == FType.MUL:
                        v = flist[0].v * flist[1].v
                    elif self.t == FType.DIV:
                        v = flist[0].v / flist[1].v
                    return (FType(v, t), 0)
                elif t == FType.VAL:
                    return (visitor.oper(flist, self), 0)
            
            else:
                raise ValueError("%s requires 2 arguments" % str(self))
        elif self.t == FType.DEREF:
            if len(flist) == 1:
                return (visitor.deref(flist[0]), 0)
            else:
                raise ValueError("%s requires 1 argument" % str(self))
        else:
            raise ValueError("unsupported operator %s" % str(self))

    #def validate_field(f):
    #    return (True if f.t in self.allow_types else False)

class Struct:
    def __init__(self, s = None):
        self.t = FType.STRUCT
        self.fields = set()
        self.cast_fields = dict()
        #self.all = False
        self.hide_fields = set()
        self.noderef_fields = set()
        if not s is None and s != "":
            fall = False
            for f in s.split(','):
                if f == "*":
                    fall = True
                elif f[0] == "!":
                    self.hide_fields.add(f[1:])
                elif f[0] == "*":
                    self.noderef_fields.add(f[1:])
                else:
                    if f[0] == "(":
                        i = f.find(")", 1)
                        if i == -1:
                            raise ValueError("unclosed ( at '%s'" % f)
                        elif i == len(f) -1:
                            raise ValueError("closed ) at '%s'" % f)
                        cast = f[1:i].strip()
                        name = f[i+1:]
                        self.fields.add(name)
                        self.cast_fields[name] = cast
                    else:
                        self.fields.add(f)
            if fall and len(self.fields) > 0:
                self.fields = set()
            #    self.all = True

    def __str__(self):
        s = ".(( "
        s += ", ".join(x for x in self.fields)
        if len(self.hide_fields) > 0:
            if len(s) > 3:
                s += ", "
            s += ", ".join("!" + x for x in self.hide_fields)
        if len(self.noderef_fields) > 0:
            if len(s) > 3:
                s += ", "
            s += ", ".join("*" + x for x in self.noderef_fields)
        s += " ))"
        return s


def operpos_init():
    #(Name, Priority, Allow_Multiply, Str)

    op_l = dict()

    op_l["*"] = Oper(FType.DEREF)
    op_l["&"] = Oper(FType.REF)

    op_l["-"] = Oper(FType.NEG)

    op_c = dict()

    op_c["*"] = Oper(FType.MUL)
    op_c["/"] = Oper(FType.DIV)

    op_c["+"] = Oper(FType.SUM)
    op_c["-"] = Oper(FType.MINUS)

    return (op_l, op_c, Oper(FType.CAST))


# Parse format
# value1 ; value2 ; struct . field1 , field2
#
# * Dereference
# & Reference
# [] Array elements with default range
# [start1:end1, start2:end2, pos, ..] Array elements in choosen ranges
# [ .. => next ] List elements with next iterator
# <s> <str> Cast as string (range like array)
# <utf8> Cast as UTF-8 string
#
#
# Filter
#
# Print array elements when > 0
# array[0:100] { _ > 0 }
#
# Print array elements - structuras fileds id, name  with id > 0
# array[0:100] { id > 0 } id, name
#
# argv[0:100] { @ _== 0 }      `argv[0]`, `argv[1]`, etc until first null
# emp[0:100] { @ code == 0 }  `emp[0]`, `emp[1]`, etc until `emp[n].code==0`
class CommandParser:
    set_sym = frozenset([ '*', '&', '+', '-', '/', '!', '@', '~', '#', '$', '%', '^', 
        '(', ')', '[', ']', '{', '}', '?', '\'', '\\', '=', '_' ])

    def __init__(self):
        (self.oper_l, self.oper_c, self.oper_cast) = operpos_init()
              
    def parse(self, arg):
        tree = list()
        lex = shlex.shlex(arg)
        s = list()
        for l in lex:
            if l == ";":
                if len(s) > 0:
                    (e, pos, pname) = self.__parse_tree(s)
                    tree.append((e, pname))
                    s = list()
            else:
                s.append(l)

        if len(s) > 0:
            (e, pos, pname) = self.__parse_tree(s)
            tree.append((e, pname))

        return tree

    def parse1(self, arg):
        lex = shlex.shlex(arg)
        s = list()
        for l in lex:
            s.append(l)

        if len(s) > 0:
            (e, pos, pname) = self.__parse_tree(s)
            return e
        else:
            return None

#
# @val arg  Tokenised string list to parse
# @val pos  Position in string
# @val sub  Token ( found
    def __parse_tree(self, s, pos = 0, sub = False):
        rp = list() # Expression in reverse polish notation
        stack = list() # Opers queue

        a = False # First argument recived
        cast = None
        end_expr = False

        carg = 0
        coper = 0

        spos = pos

        pname = list()

        print_debug(str(s), 2)

        while pos < len(s):
            if s[pos] == "(":
                is_cast = False
                if cast is None:
                    p = pos + 1
                    is_deref = False
                    while p < len(s):
                        if s[p] == ')':
                            is_cast = True
                            break
                        elif is_deref:
                            if s[p] != '*':
                                break
                        elif s[p] == '*':
                            is_deref = True
                        elif s[p] in CommandParser.set_sym:
                            break

                        p += 1

                    if is_cast:
                        cast = " ".join(str(x) for x in s[pos + 1: p])
                        pname.append("( %s )" % cast)
                        pos = p + 1
                        continue

                (rpsub, pos, psubname) = self.__parse_tree(s, pos + 1, True)
                pname.append("(")
                pname.append(psubname)
                pname.append(")")
                #pos += 1
                rp.append(Expr(rpsub))
                carg += 1
                a = True
            elif s[pos] == ")":
                if not sub:
                    raise ValueError("unhandled %s at %d" % (s[pos], pos))
                break
            elif s[pos] == "[": 
                spos = pos + 1
                found = False
                while pos < len(s):
                    if s[pos] == "]":
                        found = True
                        break
                    pos += 1

                if found:
                    rp.append(Range("".join(s[spos:pos])))
                else:
                    raise ValueError("unclosed [ at %d" % (spos - 1))
            elif s[pos] == "<": 
                spos = pos + 1
                found = False
                while pos < len(s):
                    if s[pos] == ">":
                        found = True
                        break
                    pos += 1

                if found:
                    rp.append(Transform("".join(s[spos:pos])))
                else:
                    raise ValueError("unclosed > at %d" % (spos - 1))
            elif s[pos] == "{": 
                spos = pos + 1
                found = False
                while pos < len(s):
                    if s[pos] == "}":
                        found = True
                        break
                    pos += 1

                if found:
                    coper += self.flush(rp, stack)
                    rp.append(Filter("".join(s[spos:pos])))
                    end_expr = True
                else:
                    raise ValueError("unclosed } at %d" % (spos - 1))
            elif s[pos] == "@": 
                rp.append(Filter("@_=0"))
            elif s[pos] == ".": # Structure fields
                if len(s) > pos:
                    pos += 1
                    coper += self.flush(rp, stack)
                    if s[pos] == "(" and s[pos + 1] == "(":
                        spos = pos + 2
                        found = False
                        while pos < len(s):
                            if s[pos] == ")" and s[pos + 1] == ")":
                                found = True
                                pos += 1
                                break
                            pos += 1

                        if found:
                            rp.append(Struct("".join(s[spos:pos - 1])))
                        else:
                            raise ValueError("unclosed ) at %d" % (spos - 1))
                    else:
                        rp.append(Struct(s[pos]))

                    end_expr = True
                else:
                    raise ValueError("no struct fields")
            
            elif a:
                pname.append(s[pos])
                o = self.oper_c.get(s[pos])
                if o is None:
                    if len(stack) == 0:
                        raise ValueError("too many arguments at pos %d (%s)" % (pos, s[pos]))
                    else:
                        spos = pos
                        (f, pos) = self.extract_float(s, pos)
                        if f is None:
                            rp.append(FType(s[pos]))
                        else:
                            if pos > spos:
                                del pname[-1]
                                pname.append("".join(s[spos:pos+1]))

                            rp.append(FType(f, FType.FLOAT))
                    
                        carg += 1
                        if not cast is None:
                            #print(" ".join(str(x) for x in stack))
                            self.flush_pri_left(rp, stack, self.oper_cast)
                            rp.append(FType(cast, FType.CAST))
                            cast = None
                else:
                    while len(stack) > 0 and o.pri <= stack[-1].pri:
                        o_f = stack.pop()
                        rp.append(o_f)
                        if o_f.loc == OperLoc.CENTR:
                            coper += 1
                            #print ("%d/%d %s" % (coper, carg, o_f.s))

                    if len(stack) == 0 or o.pri > stack[-1].pri:
                        if end_expr:
                            raise ValueError("no operators allowed at pos %d (%s)" % (pos, s[pos]))
                        stack.append(o)
                    else:
                        raise ValueError("'%s' not allowed at pos %d" % (s[pos], pos))
            else: # First element
                pname.append(s[pos])
                o = self.oper_l.get(s[pos])
                if o is None:
                    spos = pos
                    (f, pos) = self.extract_float(s, pos)
                    if f is None:
                        rp.append(FType(s[pos]))
                    else:
                        if pos > spos:
                            del pname[-1]
                            pname.append("".join(s[spos:pos+1]))

                        rp.append(FType(f, FType.FLOAT))
                    
                    carg += 1
                    if not cast is None:
                        self.flush_pri_left(rp, stack, self.oper_cast)
                        rp.append(FType(cast, FType.CAST))
                        cast = None

                    a = True
                elif len(stack) == 0 or (o.t == stack[-1].t and o.allow_multi):
                    if end_expr:
                        raise ValueError("no operators allowed at pos %d (%s)" % (pos, s[pos]))
                    stack.append(o)
                else:
                    raise ValueError("'%s' not allowed at pos %d" % (s[pos], pos))

            pos += 1

        if sub and (pos == len(s) or s[pos] != ")"):
            raise ValueError("unclosed ( at %d" % (spos - 1))

        if not cast is None:
            self.flush_pri_left(rp, stack, self.oper_cast)
            rp.append(FType(cast, FType.CAST))
            cast = None
        
        coper += self.flush(rp, stack)

        if coper != carg - 1:
            raise ValueError("incomplete operation (%d/%d)" % (coper, carg))

        return (rp, pos, " ".join(pname))


    r_N = re.compile(r'^\d+$')
    r_N_E = re.compile(r'^\d+[eE]$')
    r_N_E_N = re.compile(r'^\d+[eE]\d+$')

    def extract_float(self, s, pos):
        try:
            if not self.r_N.match(s[pos]) is None and pos < len(s) - 2:
                if s[pos + 1] == ".":
                    if not self.r_N.match(s[pos + 2]) is None or not self.r_N_E_N.match(s[pos + 2]) is None: 
                        fstr = s[pos] + s[pos + 1] + s[pos + 2]
                        return (float(fstr), pos + 2)
                    elif not self.r_N_E.match(s[pos + 2]) is None and s[pos + 3] in ("-", "+") \
                            and not self.r_N.match(s[pos + 4]) is None:
                        fstr = s[pos] + s[pos + 1] + s[pos + 2] + s[pos + 3] + s[pos + 4]
                        return (float(fstr), pos + 4)
            elif not self.r_N_E.match(s[pos]) is None:
                if s[pos + 1] in ("-", "+") and not self.r_N.match(s[pos + 2]) is None:
                    fstr = s[pos] + s[pos + 1] + s[pos + 2]
                    return (float(fstr), pos + 2)
            elif not self.r_N_E_N.match(s[pos]) is None:
                return (float(s[pos]), pos)
        except:
            pass

        return (None, pos)

    def flush_pri_left(self, rp, stack, o):
        while len(stack) > 0 and o.pri <= stack[-1].pri and stack[-1].loc == OperLoc.LEFT:
            o_f = stack.pop()
            rp.append(o_f)

    def flush(self, rp, stack):
        coper = 0
        while len(stack) > 0:
            o = stack.pop()
            rp.append(o)
            if o.loc == OperLoc.CENTR:
                coper += 1
        return coper

