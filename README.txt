# gdbprint

Package for browse data structuras with GDB python API

Tested Python version - 2.7 (gdb 7.6) and 3.5 (gdb 7.12)

Print local variables
  p_l
  
Print global variables
  p_g

Print variable
  p_v EXRESSION

Print variables
  p_v EXRESSION1 ; EXRESSION2 ; ..
  
Cast variable
  p_v (cast) name

Cast variable from address
  p_v (tNode *) 0x61cfc0

Dereference variable
  p_v *ptr_name

Print structure fields only
  p_v name .(( field1, field2 ))
  
Hide structure fields
  p_v name .(( !field1, !field2, .. ))
  
Don't dereference structure fields
  p_v name .(( !field1, !field2, .. ))

Print elements of iterable structuras (arrays, list, map, set, etc.) or string
  p_v name[range]
Custom ierable structuras browsed with printers API (see gdbprinters.py)
See output
  p_s p

'Debug printers' interpeted by type name
"std::tr1::unordered_set" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdUnorderedSetPrinter'>" (set)
"std::unordered_set" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdUnorderedSetPrinter'>" (set)
"std::unique_ptr" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdUniquePointerPrinter'>" (pointer)
"std::bitset" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdBitsetPrinter'>" (bitset)
"std::forward_list" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdForwardListPrinter'>" (list)
"std::stack" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdStackPrinter'>" (subtype)
"std::multimap" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdMapPrinter'>" (map)
"std::map" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdMapPrinter'>" (map)
"std::auto_ptr" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdAutoPointerPrinter'>" (pointer)
"std::weak_ptr" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdSharedPointerPrinter'>" (pointer)
"std::__cxx11::basic_string" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdStringPrinter'>" (string)
"std::deque" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdDequePrinter'>" (list_sized)
"std::tuple" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdTuplePrinter'>" (struct)
"std::basic_string" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdStringPrinter'>" (string)
"std::unordered_map" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdUnorderedMapPrinter'>" (map)
"std::array" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdArrayPrinter'>" (array)
"std::set" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdSetPrinter'>" (set)
"std::list" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdListPrinter'>" (list)
"std::vector" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdVectorPrinter'>" (array)
"std::shared_ptr" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdSharedPointerPrinter'>" (pointer)
"std::tr1::unordered_map" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdUnorderedMapPrinter'>" (map)
"std::multiset" = "<class 'gdbprint_libstdcpp.libstdcpp_v3.StdSetPrinter'>" (set)

'Debug printers typenames' need to be cast manually with <typename>
"list" = "<class 'gdbprint_c.misctypes.LinkedListPrinter'>" (list)

For example installed packages:
  gdbprint_c           C data structuras
  gdbprint_libstdcpp   GNU libstdcpp STL data structuras
  

Print default elements count (fetch_array or fetch_string)
  p_v name[]
or
  p_v name

Transform
<str>         string (char[] alredy interpreted as null-terrminated string) with codepage (if decode failed, with codepage_failback)
<utf-8>       utf-8 string (if decode failed, with codepage_failback)
<arr>         array
<simple>      Use gdb print method (via str conversion)
<raw>         Ignore registerd printers and display structure fields
<typename>    typename (for custom data structuras
  
Transform combinations
<arr,utf-8>   - array (try to interpreter char sequence as utf-8)

Print linked list with iterator next (disable dereference iterator) (by default used transform 'list' typename)
  p_v name[range --> next ].((*next))

Print linked list with custom iterator next (disable dereference iterator)
  p_v name <list> [range --> next ].((*next))

Print linked list with iterator iter.next (hide iter)
  p_v name[range --> iter.next ].((*iter))

Range format
[start:end] Range with fixed numbers
[index] One element. Equal to [index:index]
[start1:end1, start2:end2, ..] Several with fixed numbers
[start:end --> next] process linked list structure with next iterator 
[:end] Equal to [0:end]

Filter elements of iterated structure or array
{ filter } - if pass, print array or list item 
{ @ filter } - print and stop if filter is true
{ filter1 || filter2 || .. } - filter1 OR filter2 OR ..
{ filter1 } { filter2 } .. - filter1, if pass, then filter2, ..

Filter example:
{ _ = 0 }
{ _ != 0 }
{ _ > 0 }
{ _ >= 0 }
{ _ < 0 }
{ _ <= 0 }

@ Equal to { @ _ = 0 }


Options:

p_s [output_type | o] [text | named]                     Set output type
							 test - test output
							 named - named tag output (not fully tested)
p_s [debug | d] [(1 | | y | on) | (0 | n | off) (N)]     Set debug level (0 - disable)
p_s [fetch array | f a] SIZE                             Default fetch array size (by default 50)
p_s [fetch string | f s] SIZE                            Default fetch string size (by default 400)
p_s [codepage | cp] CODEPAGE [CODEPAGE_FAILBACK]         Codepage for single-byte (char) string 
                                                         Failback codepage used if codepage is UTF and conversion failed
p_s [verbose | v] [0 | 1 | 2]                            Verbose Output (by default 2) 
                                                         0 - only value, 1 - print type, 
                                                         2 - print length, 3 - also print full type (for STL). 
p_s [width | w] WIDTH                                    Row width for display simple arrays (by default 80)
p_s [depth | de] DEPTH                                   Depth for expand complex structuras in arrays and list (by default 2)

p_s [p | printers]                                       Show registered printers



Usage:
Add to .gdbinit gdbprint and custom printers packages

py import gdbprint
py import gdbprint_c
py import gdbprint_libstdcpp



Examples:
p_v num + 1                          Print numeric variables + constant
p_v num + num2                       Print sum of numeric variables
p_v num ; num2                       Print 2 variables

p_v arr[] { _ >= 67 }                Print array elements greater or equal 67
p_v ptr_arr<arr>[0:1]                Print array elements (transform from pointer or char array)

p_v ptr_arr_2d<arr>[0:1]<arr>[0:2]   Print 2d-array elements (transform from double-pointer)

p_v (int *) ptr_void + 1             Print poiter + 1 element

p_v argv<arr>[] @                    Print array elements (stop on null elements)

p_v str<utf8>[0:5]                   Print uft-8 substring
p_v str<arr,utf8>[[0:5]              Print array elements (try to decode elements sequence as uft-8)

Print linked list (with installed gdbprint_c)
p_v tNode_head <list> [-->next].((*next))
p_v tNode_head <list> [0:1 -->next].((*next)) 

Linked list from sys/queue.h (with installed gdbprint_c)
p_v msghead.tqh_first <list> [ --> next.tqe_next ] .((!next))
p_v msghead.tqh_first <list> [ --> next.tqe_next ] .((*next)) 
