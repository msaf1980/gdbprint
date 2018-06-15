# -*- coding: utf-8 -*-

name = "gdbprint"
version = "0.1.1"

import sys
import gdb
import re
import traceback

from .parser import CommandParser, Expr, ValueOut, tree_str
if sys.version_info < (3, 0, 0):
    import printcfg
else:
    from . import printcfg
from .printcfg import OutType

from .gdbutils import print_str
from .utils import print_obj
from .utils import is_true_or_num

from .gdbvalue import GdbVisitor
from .utils import show_printers

import sys

if sys.version_info < (3, 0, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')

#import libstdcpp_v3
#libstdcpp_v3.register()
#import misctypes
#misctypes.register()


class CommandParserSet(gdb.Command):
    def __init__(self):
        try:
            super (CommandParserSet, self).__init__ ("print_set",
                                                gdb.COMMAND_DATA,
                                                gdb.COMPLETE_NONE)
            gdb.execute('alias -a p_s = print_set') 
        except Exception as e:
            gdb.write(str(e) + "\n")

    def invoke (self, arg, from_tty):
        argl = arg.lower()
        if argl is None or arg in [ "", "help" ]:
            printcfg.help()
        #elif arg == "debug":
        #    printcfg.debug = True
        #elif arg == "nodebug":
        #    printcfg.debug = False
        #elif arg == "xml":
        #    printcfg.xml = True
        #elif arg == "noxml":
        #    printcfg.xml = False
        #elif arg == "pygdbmi":
        #    printcfg.pygdbmi= True
        #elif arg == "nopygdbmi":
        #    printcfg.pygdbmi = False
        elif argl in ("cp", "codepage"):
            printcfg.codepage = printcfg.codepage_default
            printcfg.codepage_failback = printcfg.codepage_default
        else:
            s = re.split(" +", argl.lower())
            if len(s) == 1:
                if s[0] in ("p", "printers"):
                    show_printers()
                    return
            elif len(s) == 2:
                if s[0] in ("o", "output_type"):
                    printcfg.out_type = OutType.from_str(s[1])
                    return
                elif s[0] in ("d", "debug"):
                    printcfg.debug = is_true_or_num(s[1])
                    return
                #elif s[0] == "xml":
                #    printcfg.xml = is_true(s[1])
                #    return
                #elif s[0] == "pygdbmi":
                #    printcfg.pygdbmi = is_true(s[1])
                #    return
                elif s[0] in ("cp", "codepage"):
                    if s[1] in ("utf-8", "utf8"):
                        if not printcfg.codepage in ("utf-8", "utf8"):
                            printcfg.codepage_failback = printcfg.codepage
                        printcfg.codepage = "utf-8"
                    else:
                        printcfg.codepage_failback = printcfg.codepage_default
                        printcfg.codepage = s[1]
                    
                    return
                elif s[0] in ("w", "width"):
                    printcfg.width = int(s[1])
                    return
                elif s[0] in ("de", "depth"):
                    printcfg.depth = int(s[1])
                    return
                elif s[0] in ("v", "verbose"):
                    printcfg.verbose = int(s[1])
                    return
            elif len(s) == 3:
                if s[0] in ("f", "fetch"):
                    if s[1] in ("a", "array"):
                        printcfg.fetch_array = int(s[2])
                        return
                    elif s[1] in ("s", "string"):
                        printcfg.fetch_string = int(s[2])
                        return
                    elif s[0] in ("cp", "codepage"):
                        if s[1] in ("utf-8", "utf8"):
                            printcfg.codepage = "utf-8"
                            printcfg.codepage_failback = s[2]
                        elif s[2] in ("utf-8", "utf8"):
                            printcfg.codepage = "utf-8"
                            printcfg.codepage_failback = s[1]
                        else:
                            gdb.write("unkown codepages sequence {:s}\n".format(arg))
            gdb.write("unkown command {:s}\n".format(arg))


class CommandParserCmd(gdb.Command):
    def __init__(self):
        
        try:
            super (CommandParserCmd, self).__init__ ("print_var",
                                                gdb.COMMAND_DATA,
                                                gdb.COMPLETE_NONE)
            gdb.execute('alias -a p_v = print_var') 
        except Exception as e:
            print_str(str(e) + "\n")

    def invoke (self, arg, from_tty):
        try:
            visitor = GdbVisitor
            tree = cmd_parse.parse(arg)
            if printcfg.debug > 0:
                for t in tree:
                    print_str("%s\n" % tree_str(t[0]))

            i = 0
            value = ValueOut()
            for t in tree:
                e = Expr(t[0])
                e.eval_print(visitor, t[1])
                i += 1
                if i < len(tree):
                    if printcfg.out_type != OutType.TEXT:
                        value.print_post("", True, True)
        except:
            if printcfg.debug:
                gdb.write(traceback.format_exc() + "\n")
            raise


class LocalCommand(gdb.Command):
    def __init__(self):
        
        try:
            super (LocalCommand, self).__init__ ("print_var_local",
                                                gdb.COMMAND_DATA,
                                                gdb.COMPLETE_NONE)
            gdb.execute('alias -a p_v_l = print_var_local') 
            gdb.execute('alias -a p_l = print_var_local') 
        except Exception as e:
            gdb.write(str(e) + "\n")

    def invoke (self, arg, from_tty):
        try:
            visitor = GdbVisitor
            visitor.print_frame(False)
        except:
            if printcfg.debug:
                gdb.write(traceback.format_exc() + "\n")
            raise


class GlobalCommand(gdb.Command):
    def __init__(self):
        
        try:
            super (GlobalCommand, self).__init__ ("print_var_global",
                                                gdb.COMMAND_DATA,
                                                gdb.COMPLETE_NONE)
            gdb.execute('alias -a p_v_g = print_var_global') 
            gdb.execute('alias -a p_g = print_var_global') 
        except Exception as e:
            gdb.write(str(e) + "\n")

    def invoke (self, arg, from_tty):
        try:
            visitor = GdbVisitor
            visitor.print_frame(True)
        except:
            if printcfg.debug:
                gdb.write(traceback.format_exc() + "\n")
            raise


print_str("load %s %s\n" % (name, version))
cmd_parse = CommandParser()
CommandParserSet()
CommandParserCmd()
LocalCommand()
GlobalCommand()

