from distutils.cmd import Command
from setuptools import setup
from distutils.command.clean import clean

class RunTests(Command):
    user_options=[]
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        from subprocess import Popen, PIPE, call
        from os import getcwd, execlp, chdir, path
        import re
        cdir = path.dirname(path.realpath(__file__))
        cwd = path.join(cdir, 'tests')
        chdir(cwd)
        call(["make"])
        for test in ['test_testout', 'test_testout_v2']:
            print(test)
            test = path.join(cwd, test)
            fg = open(test+'.gdb', 'r')
            fi = open(test+'.in', 'w')
            fo = open(test+'.out', 'w')
            for l in fg:
                if l.startswith('(gdb) '):
                    fi.write(l[6:])
                else:
                    fo.write(l)
            fg.close()
            fi.close()
            fo.close()
            p=Popen(['gdb', '-batch', '-n', '-x', test + '.in'], cwd=cwd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            (o,e)=p.communicate()
            err = re.sub(r'warning: .*\n', '', e)
            err = re.sub(r'[ \t]+\n', '', err)
            err = re.sub(r'\n', '', err)
            if err: raise Exception(e)
            o = re.sub(r'(=.*) 0x[0-9a-f]+', r'\1 0xXXXXX', o)
            o = re.sub(r'Temporary breakpoint 1 at .*\n', '', o)
            o = re.sub(r'Breakpoint [0-9]+ at 0x[0-9a-f]+:', 'Breakpoint:', o)
            o = re.sub(r'Breakpoint [0-9]+, main \(argc=1, argv=0x[0-9a-f]+\) at', 'Breakpoint 1, main at', o)
            o = re.sub(r'[0-9]+[ \t]+return 0;', '', o)
            o = re.sub(r'0x[0-9a-f]*[1-9a-f]+[0-9a-f]*', '0xHEX', o)
            o = re.sub(r'"argv" = \(char \*\*\) <0xHEX> { ptr = <0xHEX> { str_len:\d+ ', '"argv" = (char **) <0xHEX> { ptr = <0xHEX> { str_len:N ', o)
            o = re.sub(cdir, '', o)
            with open(test + '.reject', 'w') as f: f.write(o)
            call([ 'diff', '-u', test + '.out', test + '.reject' ])


class RunClean(clean):
    def run(self):
        global pname
        from subprocess import Popen, PIPE, call
        from os import getcwd, chdir, path
        from os import remove
        import glob
        import shutil
        c = clean(self.distribution)
        c.all = True
        c.finalize_options()
        c.run()
        cdir = path.dirname(path.realpath(__file__))
        for f in glob.glob(path.join(cdir, pname, "*.pyc")):
            remove(f)
        shutil.rmtree(path.join(cdir, 'build'), ignore_errors=True)
        shutil.rmtree(path.join(cdir, 'dist'), ignore_errors=True)
        shutil.rmtree(path.join(cdir, pname + '.egg-info'), ignore_errors=True)
        shutil.rmtree(path.join(cdir, pname, '__pycache__'), ignore_errors=True)
        cwd = path.join(cdir, 'tests')
        chdir(cwd)
        call([ 'make', 'clean' ])


if __name__ == '__main__':

    pname = 'gdbprint'

    setup(name=pname,
        version='0.1.1',
        description='GDB data structuras browser with Python API',
        url='http://github.com/msaf1980/gdbprint',
        author='Michail Safronov',
        author_email='msaf1980@gmail.com',
        license='MIT',
        packages=[pname],
        zip_safe=True,
        cmdclass={
            'test': RunTests,
            'clean': RunClean
        },
)
