from distutils.core import setup, Extension
import scorep.helper

(include, lib, lib_dir, macro, linker_flags, cc, cxx) = scorep.helper.generate_compile_deps()


cmodules = []
cmodules.append(Extension('scorep.scorep_bindings',
                          include_dirs=include,
                          libraries=[],
                          extra_compile_args=["-std=c++11"],
                          sources=['src/scorep.cpp']))


setup(
    name='scorep',
    version='1.2',
    description='This is a scorep tracing package for python',
    author='Andreas Gocht',
    author_email='andreas.gocht@tu-dresden.de',
    url='https://github.com/score-p/scorep_binding_python',
    long_description='''
This package allows tracing of python code using Score-P.
A working Score-P version is required.
For MPI tracing it uses LD_PREALOAD.
Besides this, it uses the traditional python-tracing infrastructure.
''',
    packages=['scorep'],
    ext_modules=cmodules
)
