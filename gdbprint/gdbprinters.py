import gdb

from .gdbutils import print_str
from .utils import print_debug
from .utils import DisplayType
from .define import uchr

#  ##Base class
#class DebugPrinter(object):
# 
#    ## Initializer
#    def __init__(self, value,  type):
#       ## Native value
#        self.value = value
#       ## Native value type
#        self.type = type
#       ## Array with service fields like iterators
#       ## Set if needed process it when read elements
#       self.serv_fields = []

        
        
#class NewPrinter(DebugPrinter):
#   ##array with type names
#    names = [ "type" ]
#
#  ##type name
#  typename = "typename"
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#
#    ## Set methods reuired for display_hint()


#class ListPrinter(DebugPrinter):
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.LIST
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#        self.seek_first()
#
#    ## Seek to first element    
#    def seek_first(self):
#        ..
#    ## Return current element and Iterate to next
#    def next(self):
#        ..
#       return (index, value)
#
#    ## Current position
#    def get_pos(self):
#       return index
#


#class ListSizedPrinter(DebugPrinter):
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.LIST_SIZED
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#        self.seek_first()
#
#    ## Seek to first element    
#    def seek_first(self):
#        ..
#    ## Return current element and Iterate to next
#    def next(self):
#        ..
#       return (index, value)
#
#    ## Current position
#    def get_pos(self):
#       return index
#
#   ## Return list size
#    def size(self):
#        ..
#        return size


#class StringPrinter(DebugPrinter):
#  
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.STRING
#
#    ## return string length and reserved capacity
#    def size(self):
#        ..
#        return (length,  capacity)
#
#    ## Return string
#    def string(self):
#        ..
#        return str
#
#    ## Return substring
#    def substring(self,  start, end = -1):
#        ..
#        return str[int(start):int(end)]
#
#    ## Check True if unicode
##   def is_unicode(self):
#        ..


#class StructPrinter(DebugPrinter):
#
#     ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.STRUCT
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#        self.seek_first()
#
#    ## Seek to first element    
#    def seek_first(self):
#        ..
#    ## Return current element and Iterate to next
#    def next(self):


#class ArrayPrinter(DebugPrinter):
#    
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.ARRAY
#        
#    ## Return vector length and reserved capacity
#    def size(self):
#        ..
#        return (length,  capacity)
#
#    ## Return vector[index]
#    def get(self, index):
#        ..
#       return vector[index]
            

#class NewSubTypePrinter(SubTypePrinter):
#    names = [ "type" ]
#    fields = { "field1",   "field2" }
    
  
#class SetPrinter(DebugPrinter):
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.SET
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#        self.seek_first()
#
#    ## Seek to first element    
#    def seek_first(self):
#        ..
#    ## Return current element and Iterate to next
#    def next(self):
#        ..
#       return value
#    ## Return size
#
#    def size(self):
#       return size
#
#    ## Current position
#    def get_pos(self):
#       return index
#

#class MapPrinter(DebugPrinter):
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.MAP
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#        self.seek_first()
#
#    ## Seek to first element    
#    def seek_first(self):
#        ..
#    ## Return current element and Iterate to next
#    def next(self):
#        ..
#       return (key, value)
#
#    ## Return size
#    def size(self):
#       return size
#
#    ## Current position
#    def get_pos(self):
#       return index
#
 
 #class BitsetPrinter(DebugPrinter):
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.BITSET
#
#    ## Initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#        ..
#   ## Return array with turple (index, value)
#    def get(self,  start,  count):
#        result = []
#        while  ..
#           ..   
#           result.append((index, value))
#        return result

 
#class PointerPrinter(DebugPrinter):
#
#    ## Display type
#    @staticmethod
#    def display_hint():
#        return  DisplayType.PTR
#
#   ## Optional initializer
#    def __init__ (self, value,  type):
#        DebugPrinter.__init__(self,  value,  type)
#
#    ## Return pointer value: turple (ptr, descr)
#    def ptr (self):
        
def short_name(fullname):
        i = fullname.find("<")
        if i > 0:
                return fullname[:i]
        else:
                return fullname

def p_name(fullname):
        i = fullname.find("<")
        e = fullname.rfind(">")
        if i > 0 and e > 0 and i < e:
            r1 = fullname.find(", ", i)
            if r1 == -1:
                return fullname
            r2 = fullname.find(", ", r1)
            if r2 == -1:
                return fullname
            r2 = fullname.find("<", i+1)
            if r2 == -1:
                return fullname
            name = fullname[:i+1]
            end = fullname[e:]
            param = fullname[i+1:r1]
            return name + param + ", .."+ end
        else:
            return fullname


class DebugPrinter(object):
    
    def __init__(self, value,  type):
        self.value = value
        self.type = type
        self.serv_fields = None
               
    @staticmethod
    def name(fullname):
        i = fullname.find("<")
        if i > 0:
            return fullname[:i]
        else:
            return None
    
    @staticmethod
    def display_hint():
        raise NotImplementedError("display_hint") 

        
# For custom types, interpreted as structuras
class SubTypePrinter(DebugPrinter):
    fields = { }

    @staticmethod
    def display_hint():
        return  DisplayType.SUBTYPE


#return string_array, read, read_str_length (if NULL found)
def read_string(nvalue, start,  end):
    #print(str(start) + ":" + str(end))
    if end == -1 or nvalue is None:
        return (None, -1, None)
    i = start
    target_array = bytearray()
    str_length = None
    if nvalue.type.code == gdb.TYPE_CODE_PTR:
        ptr = nvalue.dereference()
        if ptr.address == 0:
            return (None, 0, 0)
        target_type = str(ptr.type)
    else:    
        target_type = str(nvalue[0].type)
    while i <= end:
        if nvalue.type.code == gdb.TYPE_CODE_PTR:
            elem = (nvalue + i).dereference()
        else:    
            elem = nvalue[i]
        if elem is None or elem == 0:
            str_length = i
            i += 1
            break
        if elem < 0:
            elem += 256
        #target_array += chr(elem).decode(printcfg.codepage)
        target_array.append(int(elem))
        i += 1
    #print("read :" + str(i-1))
    return (target_array,  i-1,  str_length)

#return string_array, read, read_str_length (if NULL found)
def read_unicode(nvalue, start,  end):
    #print(str(start) + ":" + str(end))
    if end == -1 or nvalue is None:
        return (None, -1, None)
    i = start
    target_array = ""
    str_length = None
    while i <= end:
        if nvalue.type.code == gdb.TYPE_CODE_PTR:
            elem = (nvalue + i).dereference()
        else:    
            elem = nvalue[i]
        if elem is None or elem == 0:
            str_length = i
            i += 1
            break
        target_array += uchr(elem)
        i += 1
    #print("read :" + str(i-1))
    return (target_array,  i-1,  str_length)

