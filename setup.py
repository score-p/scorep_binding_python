from distutils.core import setup, Extension
import scorep.helper

if scorep.helper.get_scorep_version() < 5.0:
    raise RuntimeError(
        "Score-P version less than 5.0, plase use Score-P >= 5.0")

link_mode = scorep.helper.get_scorep_link_mode()
if not ("shared=yes" in link_mode):
    raise RuntimeError(
        "Score-P not build with \"--enable-shared\". Link mode is:\n{}".format(link_mode))


cmodules = []
(include, _, _, _, _) = scorep.helper.generate_compile_deps()
cmodules.append(Extension('scorep.scorep_bindings',
                          include_dirs=include,
                          libraries=[],
                          extra_compile_args=["-std=c++11"],
                          sources=['src/scorep.cpp']))

setup(
    name='scorep',
    version='3.0',
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
    packages=['scorep', 'scorep.instrumenters'],
    ext_modules=cmodules
)
