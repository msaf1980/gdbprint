(gdb) file test
(gdb) py sys.path.insert(0, '..')
(gdb) py import gdbprint
load gdbprint 0.1.1
(gdb) break 91
(gdb) run
Breakpoint: file test.cpp, line 91.

Breakpoint 1, main at test.cpp:91

(gdb) p_s verbose 2
(gdb) p_s w 0
(gdb) p_l
frame = "main(int, char**)" {
    "act" = (action) EXIT (0),
    "argc" = (int) 1,
    "argv" = (char **) <0xHEX> { ptr = <0xHEX> { str_len:N [0:399] = "/tests/test" + \0 } },
    "arr_2d" = (int [2][3]) <0xHEX> {
        [0] = (int [3]) <0xHEX> {
            [0] = 1,
            [1] = 2,
            [2] = 3,
        },
        [1] = (int [3]) <0xHEX> {
            [0] = 4,
            [1] = 5,
            [2] = 6,
        },
    },
    "b" = (bool) true,
    "base" = (char *) <0xHEX> { str_len:15 [0:399] = "Василий Vasiliy" + \0 },
    "dnum" = (double) 1.23e+21,
    "fnum" = (float) 1.23000005e+21,
    "n" = (unsigned long) 2,
    "num" = (unsigned long) 0,
    "ptr_arr" = (int *) <0xHEX> { ptr = 10 },
    "ptr_arr_2d" = (int **) <0xHEX> { ptr = <0xHEX> { ptr = 1 } },
    "ptr_fnum" = (float *) <0xHEX> { ptr = 1.23000005e+21 },
    "ptr_null" = (int *) <0x0>,
    "ptr_void_arr_2d" = (void *) <0xHEX>,
    "size" = (unsigned long) 1,
    "st_p_arr" = (st_p [2]) <0xHEX> {
        [0] = (st_p) <0xHEX> {
            "start" = (char *) <0xHEX> { str_len:15 [0:399] = "Василий Vasiliy" + \0 },
            "end" = (char *) <0xHEX> { str_len:13 [0:399] = "силий Vasiliy" + \0 }
        },
        [1] = (st_p) <0xHEX> {
            "start" = (char *) <0xHEX> { str_len:13 [0:399] = "силий Vasiliy" + \0 },
            "end" = (char *) <0xHEX> { str_len:12 [0:399] = "илий Vasiliy" + \0 }
        },
    },
    "st_ptr" = (st *) <0xHEX> { ptr =  {
        "i" = (int) 1000,
        "ui" = (unsigned int) 1000,
        "l" = (long) 1000,
        "ul" = (unsigned long) 1000,
        "f" = (float) 1000,
        "d" = (double) 1000
    } },
    "st_void_2ptr" = (void **) <0xHEX> { ptr = (void *) <0xHEX> },
    "st_void_ptr" = (void *) <0xHEX>,
    "str" = (char *) <0xHEX> { str_len:42 [0:399] = "Р’Р°СЃРёР»РёР№ РџСѓРїРєРёРЅ Vasiliy Pupkin" + \0 },
    "str1251" = (char [16]) <0xHEX> { str_len:15 [0:15] = "Василий Vasiliy" + \0 },
    "struct_ex" = (st) <0xHEX> {
        "i" = (int) 1000,
        "ui" = (unsigned int) 1000,
        "l" = (long) 1000,
        "ul" = (unsigned long) 1000,
        "f" = (float) 1000,
        "d" = (double) 1000
    },
    "u" = (ub) <0xHEX> {
        "i" = (unsigned int) 4294901760,
        "b" = (unsigned char [4]) <0xHEX> { str_len:0 [0:3] = "" + \0 }
    },
    "wstr" = (wchar_t *) <0xHEX> { str_len:30 [0:399] = L"Василий Пупкин, Vasiliy Pupkin" + \0 },
}
(gdb) p_g
frame = "global" {
    "gl_arr" = (int [12]) <0xHEX> {
        [0] = 10,
        [1] = 11,
        [2] = 124,
        [3] = 5,
        [4] = 15,
        [5] = 67,
        [6] = 1235,
        [7] = 1034567,
        [8] = 8765,
        [9] = 145,
        [10] = 1347,
        [11] = 1,
    },
    "gl_arr_d" = (double [12]) <0xHEX> {
        [0] = 1.0000000000010278e+32,
        [1] = 11.090000001,
        [2] = 124.00670000000009,
        [3] = 5,
        [4] = 15,
        [5] = 67,
        [6] = 1235,
        [7] = 1034567,
        [8] = 8765,
        [9] = 145,
        [10] = 1347,
        [11] = 1.0017171444111113,
    },
    "gl_arr_f" = (float [12]) <0xHEX> {
        [0] = 1.00000003e+32,
        [1] = 11.0900002,
        [2] = 124.006699,
        [3] = 5,
        [4] = 15,
        [5] = 67,
        [6] = 1235,
        [7] = 1034567,
        [8] = 8765,
        [9] = 145,
        [10] = 1347,
        [11] = 1.00171709,
    },
}
(gdb) p_v 1
"1" = 1
(gdb) p_v 1 + (3 * 2)
"1 + ( 3 * 2 )" = 7
(gdb) p_v num + 1
"num + 1" = (unsigned long) 1
(gdb) p_v num + dnum
"num + dnum" = (double) 1.23e+21
(gdb) p_v *ptr_fnum
"* ptr_fnum" = (float) 1.23000005e+21
(gdb) p_v (st *) st_void_ptr
"( st * ) st_void_ptr" = (st *) <0xHEX> { ptr =  {
    "i" = (int) 1000,
    "ui" = (unsigned int) 1000,
    "l" = (long) 1000,
    "ul" = (unsigned long) 1000,
    "f" = (float) 1000,
    "d" = (double) 1000
} }
(gdb) p_v gl_arr[] { _ >= 67 }
"gl_arr" = (int [12]) <0xHEX> {
    [2] = 124,
    [5] = 67,
    [6] = 1235,
    [7] = 1034567,
    [8] = 8765,
    [9] = 145,
    [10] = 1347,
}
(gdb) p_v gl_arr_d[] { _ >= 67 }
"gl_arr_d" = (double [12]) <0xHEX> {
    [0] = 1.0000000000010278e+32,
    [2] = 124.00670000000009,
    [5] = 67,
    [6] = 1235,
    [7] = 1034567,
    [8] = 8765,
    [9] = 145,
    [10] = 1347,
}
(gdb) p_v ptr_arr_2d<arr>[0:1]<arr>[0:2]
"ptr_arr_2d" = (int **) <0xHEX> {
    [0] = (int *) <0xHEX> {
        [0] = 1,
        [1] = 2,
        [2] = 3,
    },
    [1] = (int *) <0xHEX> {
        [0] = 4,
        [1] = 5,
        [2] = 6,
    },
}
(gdb) p_v 1 + (int **)ptr_void_arr_2d
"1 + ( int * * ) ptr_void_arr_2d" = (int **) <0xHEX> { ptr = <0xHEX> { ptr = 4 } }
(gdb) p_v (int **)ptr_void_arr_2d<arr>[0:1]<arr>[0:2]
"( int * * ) ptr_void_arr_2d" = (int **) <0xHEX> {
    [0] = (int *) <0xHEX> {
        [0] = 1,
        [1] = 2,
        [2] = 3,
    },
    [1] = (int *) <0xHEX> {
        [0] = 4,
        [1] = 5,
        [2] = 6,
    },
}
(gdb) p_v *str
"* str" = (char) 208 "Р"
(gdb) p_v wstr
"wstr" = (wchar_t *) <0xHEX> { str_len:30 [0:399] = L"Василий Пупкин, Vasiliy Pupkin" + \0 }
(gdb) p_v wstr[1:4]
"wstr" = (wchar_t *) <0xHEX> { [1:4] = L"асил" }
(gdb) p_v wstr[1:4, 8]
"wstr" = (wchar_t *) <0xHEX> {
    { [1:4] = L"асил" },
    { [8] = L"П" }
}
(gdb) p_v wstr<arr>[0:19]
"wstr" = (wchar_t *) <0xHEX> {
    [0] = 1042 L'В',
    [1] = 1072 L'а',
    [2] = 1089 L'с',
    [3] = 1080 L'и',
    [4] = 1083 L'л',
    [5] = 1080 L'и',
    [6] = 1081 L'й',
    [7] = 32 L' ',
    [8] = 1055 L'П',
    [9] = 1091 L'у',
    [10] = 1087 L'п',
    [11] = 1082 L'к',
    [12] = 1080 L'и',
    [13] = 1085 L'н',
    [14] = 44 L',',
    [15] = 32 L' ',
    [16] = 86 L'V',
    [17] = 97 L'a',
    [18] = 115 L's',
    [19] = 105 L'i',
}
(gdb) p_v wstr<arr>[1:4, 8]
"wstr" = (wchar_t *) <0xHEX> {
    [1] = 1072 L'а',
    [2] = 1089 L'с',
    [3] = 1080 L'и',
    [4] = 1083 L'л',
    [8] = 1055 L'П',
}
(gdb) p_v str<utf8>
"str" = (char *) <0xHEX> { str_len:42 [0:399] = utf-8:"Василий Пупкин Vasiliy Pupkin" + \0 }
(gdb) p_v str<utf8>[1:4]
"str" = (char *) <0xHEX> { [1:4] = 1251:"’Р°С" }
(gdb) p_v str<utf8>[0:5, 8]
"str" = (char *) <0xHEX> {
    { [0:5] = utf-8:"Вас" },
    { [8] = 1251:"Р" }
}
(gdb) p_v str<arr,utf8>[0:5]
"str" = (char *) <0xHEX> {
    [0] = 208 "Р",
    [1] = 146 "’" utf-8:"В",
    [2] = 208 "Р",
    [3] = 176 "°" utf-8:"а",
    [4] = 209 "С",
    [5] = 129 "Ѓ" utf-8:"с",
}
(gdb) p_v str<arr,utf8>[0:5, 8]
"str" = (char *) <0xHEX> {
    [0] = 208 "Р",
    [1] = 146 "’" utf-8:"В",
    [2] = 208 "Р",
    [3] = 176 "°" utf-8:"а",
    [4] = 209 "С",
    [5] = 129 "Ѓ" utf-8:"с",
    [8] = 208 "Р",
}
(gdb) p_v str1251
"str1251" = (char [16]) <0xHEX> { str_len:15 [0:15] = "Василий Vasiliy" + \0 }
(gdb) p_v str1251[1:4]
"str1251" = (char [16]) <0xHEX> { [1:4] = "асил" }
(gdb) p_v str1251[0:5, 8]
"str1251" = (char [16]) <0xHEX> {
    { [0:5] = "Васили" },
    { [8] = "V" }
}
(gdb) p_v str1251<arr>[0:5]
"str1251" = (char [16]) <0xHEX> {
    [0] = 194 "В",
    [1] = 224 "а",
    [2] = 241 "с",
    [3] = 232 "и",
    [4] = 235 "л",
    [5] = 232 "и",
}
(gdb) p_v str1251<arr>[0:5, 8]
"str1251" = (char [16]) <0xHEX> {
    [0] = 194 "В",
    [1] = 224 "а",
    [2] = 241 "с",
    [3] = 232 "и",
    [4] = 235 "л",
    [5] = 232 "и",
    [8] = 86 "V",
}
(gdb) p_v wstr[n-1:n*2]
"wstr" = (wchar_t *) <0xHEX> { [1:4] = L"асил" }
