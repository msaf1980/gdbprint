# -*- coding: utf-8 -*-

import gdb
import re
import traceback

from parser import CommandParser, Expr, tree_str
import config
from config import OutType

from gdbutils import print_str
from utils import print_obj
from utils import is_true_or_num

from gdbvalue import GdbVisitor
from utils import show_printers

import sys
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
            config.help()
        #elif arg == "debug":
        #    config.debug = True
        #elif arg == "nodebug":
        #    config.debug = False
        #elif arg == "xml":
        #    config.xml = True
        #elif arg == "noxml":
        #    config.xml = False
        #elif arg == "pygdbmi":
        #    config.pygdbmi= True
        #elif arg == "nopygdbmi":
        #    config.pygdbmi = False
        elif argl in ("cp", "codepage"):
            config.codepage = config.codepage_default
            config.codepage_failback = config.codepage_default
        else:
            s = re.split(" +", argl.lower())
            if len(s) == 1:
                if s[0] in ("p", "printers"):
                    show_printers()
                    return
            elif len(s) == 2:
                if s[0] in ("o", "output_type"):
                    config.out_type = OutType.from_str(s[1])
                    return
                elif s[0] in ("d", "debug"):
                    config.debug = is_true_or_num(s[1])
                    return
                #elif s[0] == "xml":
                #    config.xml = is_true(s[1])
                #    return
                #elif s[0] == "pygdbmi":
                #    config.pygdbmi = is_true(s[1])
                #    return
                elif s[0] in ("cp", "codepage"):
                    if s[1] in ("utf-8", "utf8"):
                        if not config.codepage in ("utf-8", "utf8"):
                            config.codepage_failback = config.codepage
                        config.codepage = "utf-8"
                    else:
                        config.codepage_failback = config.codepage_default
                	config.codepage = s[1]
                    
                    return
                elif s[0] in ("w", "width"):
                    config.width = int(s[1])
                    return
                elif s[0] in ("de", "depth"):
                    config.depth = int(s[1])
                    return
                elif s[0] in ("v", "verbose"):
                    config.verbose = int(s[1])
                    return
            elif len(s) == 3:
                if s[0] in ("f", "fetch"):
                    if s[1] in ("a", "array"):
                        config.fetch_array = int(s[2])
                        return
                    elif s[1] in ("s", "string"):
                        config.fetch_string = int(s[2])
                        return
                    elif s[0] in ("cp", "codepage"):
                        if s[1] in ("utf-8", "utf8"):
                            config.codepage = "utf-8"
                            config.codepage_failback = s[2]
                        elif s[2] in ("utf-8", "utf8"):
                            config.codepage = "utf-8"
                            config.codepage_failback = s[1]
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
        global gdb_var
        try:
            visitor = GdbVisitor()
            tree = cmd_parse.parse(arg)
            if config.debug:
                for t in tree:
                    print_str("%s\n" % tree_str(t[0]))

            i = 0
            for t in tree:
                e = Expr(t[0])
                e.eval_print(visitor, t[1])
                i += 1
                if i < len(tree):
                    print_str(",\n")
        except:
            if config.debug:
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
        global gdb_var
        try:
            #gdb_var.frame_eval_and_print(False, arg)
            cmd_parse = CommandParser()
            cmd_parse.parse(arg)
        except:
            if config.debug:
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

    #def invoke (self, arg, from_tty):
        #global gdb_var
        #try:
        #    gdb_var.frame_eval_and_print(True, arg)
        #except:
        #    if config.debug:
        #        gdb.write(traceback.format_exc() + "\n")
        #    raise

cmd_parse = CommandParser()
CommandParserSet()
CommandParserCmd()
LocalCommand()
GlobalCommand()

