#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <wchar.h>
#include <stdlib.h>
#include <errno.h>

typedef struct st {
	int i;
	unsigned ui;
	long l;
	unsigned long ul;
	float f;
	double d;
} st;

union ub {
    unsigned int i;
    unsigned char b[4];
};

enum action { EXIT, SLEEP, RECURSE, OVERFLOW, NULL_PTR };

int gl_arr[] =  { 10, 11, 124, 5, 15, 67, 1235, 1034567, 8765, 145, 1347, 1 };
float gl_arr_f[] =  { 100000000000102776200000018282828.006, 11.090000001, 124.0067000000001, 5, 15, 67, 1235, 1034567, 8765, 145, 1347, 1.001717144411111190000001 };
double gl_arr_d[] =  { 100000000000102776200000018282828.006, 11.090000001, 124.0067000000001, 5, 15, 67, 1235, 1034567, 8765, 145, 1347, 1.001717144411111190000001 };

int main(int argc, char* argv[]) {
	int *ptr_arr = gl_arr;


        int arr_2d[2][3] = {
            { 1, 2, 3 },
            {4, 5, 6}
        };
        int *ptr_null = NULL;
        int **ptr_arr_2d = (int **) arr_2d;
        void *ptr_void_arr_2d = ptr_arr_2d;

	bool b = true;
        action act = EXIT;

	wchar_t *wstr = L"Василий Пупкин, Vasiliy Pupkin";
	/* UTF-8 */
	char *str = "Василий Пупкин Vasiliy Pupkin";
	/* In cp1251 "Василий Vasiliy" */
	char str_array[] = { (char) 194, (char) 224, (char) 241, (char) 232, (char) 235, (char) 232, (char) 233, (char) 32, 'V', 'a', 's', 'i', 'l', 'i', 'y', (char) 0 };

        ub u;
        u.b[0] = 0;
        u.b[1] = 0;
        u.b[2] = 255;
        u.b[3] = 255;


	unsigned long num = 0;
        float fnum = 1230000000000000000001.02;
        float *ptr_fnum = &fnum;
        double dnum = 1230000000000000000001.02;

        st struct_ex;
        struct_ex.i = 1000;
        struct_ex.ui = 1000;
        struct_ex.l = 1000L;
        struct_ex.ul = 1000L;
        struct_ex.f = 1000.0F;
        struct_ex.d = 1000.0D;
        void *st_void_ptr = &struct_ex;
        void **st_void_2ptr = &st_void_ptr;
        st *st_ptr = &struct_ex;

	return 0;
}

