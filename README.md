# gdbprint

Package for browse data structuras with GDB python API

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

Print default elements count (fetch_array or fetch_string)
  p_v name[]
or
  p_v name

Print linked list with iterator next (disable dereference iterator)
  p_v name[range --> next ].((*next))
  
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

Transform
<str>         string (char[] alredy interpreted as null-terrminated string) with codepage (if decode failed, with codepage_failback)
<utf-8>       utf-8 string (if decode failed, with codepage_failback)
<arr>         array

Transform combinations
<arr,utf-8>   - array (try to interpreter char sequence as utf-8)

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

Print linked list
p_v tNode_head <list> [-->next].((*next))
p_v tNode_head <list> [0:1 -->next].((*next)) 

Linked list from sys/queue.h
p_v msghead.tqh_first <list> [ --> next.tqe_next ] .((!next))
p_v msghead.tqh_first <list> [ --> next.tqe_next ] .((*next))
