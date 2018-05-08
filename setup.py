#
# Copyright 2017, Technische Universitaet Dresden, Germany, all rights reserved.
# Author: Andreas Gocht
#
# Permission to use, copy, modify, and distribute this Python software and
# its associated documentation for any purpose without fee is hereby
# granted, provided that the above copyright notice appears in all copies,
# and that both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of TU Dresden is not used in
# advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.


from distutils.core import setup, Extension
from distutils.command.install import install
from distutils.command.install_data import install_data
import distutils.ccompiler

import os
import subprocess
import re
import sys
import stat
import platform
import functools
import scorep.helper 

scorep_config = [
    "scorep-config",
    "--compiler",
    "--user",
    "--thread=pthread",
    "--mpp=none"]
scorep_config_mpi = [
    "scorep-config",
    "--compiler",
    "--user",
    "--thread=pthread",
    "--mpp=mpi"]


def get_config(scorep_config):
    (retrun_code, _, _) = scorep.helper.call(scorep_config + ["--cuda"])
    if retrun_code == 0:
        scorep_config.append("--cuda")
        print("Cuda is supported, building with cuda")
    else:
        print("Cuda is not supported, building without cuda")
        scorep_config.append("--nocuda")

    (retrun_code, _, _) = scorep.helper.call(scorep_config + ["--opencl"])
    if retrun_code == 0:
        scorep_config.append("--opencl")
        print("OpenCL is supported, building with OpenCL")
    else:
        print("OpenCl is not supported, building without OpenCL")
        scorep_config.append("--noopencl")

    (_, ldflags, _) = scorep.helper.call(scorep_config + ["--ldflags"])
    (_, libs, _) = scorep.helper.call(scorep_config + ["--libs"])
    (_, mgmt_libs, _) = scorep.helper.call(scorep_config + ["--mgmt-libs"])
    (_, cflags, _) = scorep.helper.call(scorep_config + ["--cflags"])

    (_, scorep_adapter_init, _) = scorep.helper.call(scorep_config + ["--adapter-init"])

    libs = libs + " " + mgmt_libs

    lib_dir = re.findall(" -L[/+-@.\w]*", ldflags)
    lib = re.findall(" -l[/+-@.\w]*", libs)
    include = re.findall(" -I[/+-@.\w]*", cflags)
    macro = re.findall(" -D[/+-@.\w]*", cflags)
    linker_flags = re.findall(" -Wl[/+-@.\w]*", ldflags)

    def remove_flag3(x): return x[3:]

    def remove_space1(x): return x[1:]

    lib_dir = list(map(remove_flag3, lib_dir))
    lib = list(map(remove_space1, lib))
    include = list(map(remove_flag3, include))
    macro = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags))

    macro = list(map(lambda x: tuple([x, 1]), macro))

    return (include, lib, lib_dir, macro, linker_flags, scorep_adapter_init)


def get_mpi_config():
    (_, mpi_version, mpi_version2) = scorep.helper.call(["mpiexec", "--version"])
    mpi_version = mpi_version + mpi_version2
    if "OpenRTE" in mpi_version:
        print("OpenMPI detected")
        (_, ldflags, _) = scorep.helper.call(["mpicc", "-showme:link"])
        (_, compile_flags, _) = scorep.helper.call(["mpicc", "-showme:compile"])
    elif ("Intel" in mpi_version) or ("MPICH" in mpi_version):
        print("Intel or MPICH detected")
        (_, ldflags, _) = scorep.helper.call(["mpicc", "-link_info"])
        (_, compile_flags, _) = scorep.helper.call(["mpicc", "-compile_info"])
    else:
        print("cannot determine mpi version: \"{}\"".format(mpi_version))
        exit(-1)

    lib_dir = re.findall(" -L[/+-@.\w]*", ldflags)
    lib = re.findall(" -l[/+-@.\w]*", ldflags)
    include = re.findall(" -I[/+-@.\w]*", compile_flags)
    macro = re.findall(" -D[/+-@.\w]*", compile_flags)
    linker_flags = re.findall(" -Wl[/+-@.\w]*", ldflags)
    linker_flags_2 = re.findall(" -Xlinker [/+-@.\w]*", ldflags)

    def remove_flag3(x): return x[3:]

    def remove_x_linker(x): return x[10:]

    def remove_space1(x): return x[1:]

    lib_dir = list(map(remove_flag3, lib_dir))
    lib = list(map(remove_space1, lib))
    include = list(map(remove_flag3, include))
    macro = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags))
    linker_flags_2 = list(map(remove_x_linker, linker_flags_2))

    macro = list(map(lambda x: tuple([x, 1]), macro))

    linker_flags.extend(linker_flags_2)

    return (include, lib, lib_dir, macro, linker_flags)


(include, lib, lib_dir, macro, linker_flags_tmp,
 scorep_adapter_init) = get_config(scorep_config)
(include_mpi, lib_mpi, lib_dir_mpi, macro_mpi, linker_flags_mpi_tmp,
 scorep_adapter_init_mpi) = get_config(scorep_config_mpi)
(include_mpi_, lib_mpi_, lib_dir_mpi_, macro_mpi_,
 linker_flags_mpi_tmp_) = get_mpi_config()

# add -Wl,-no-as-needed to tell the compiler that we really want to link these. Actually this sould be default.
# as distutils adds extra args at the very end we need to add all the libs
# after this and skipt the libs later in the extension module
linker_flags = ["-Wl,-no-as-needed"]
linker_flags.extend(lib)
linker_flags.extend(linker_flags_tmp)

include_mpi.extend(include_mpi_)
lib_dir_mpi.extend(lib_dir_mpi_)
macro_mpi.extend(macro_mpi_)

linker_flags_mpi = ["-Wl,-no-as-needed"]
linker_flags_mpi.extend(linker_flags_mpi_tmp)
linker_flags_mpi.extend(linker_flags_mpi_tmp_)
linker_flags_mpi.extend(lib_mpi)
linker_flags_mpi.extend(lib_mpi_)

with open("./scorep_init.c", "w") as f:
    f.write(scorep_adapter_init)

with open("./scorep_init_mpi.c", "w") as f:
    f.write(scorep_adapter_init_mpi)

# build scorep with mpi for ld_prealod

mpi_lib_name = scorep.helper.gen_mpi_lib_name()

cc = distutils.ccompiler.new_compiler()
cc.compile(["./scorep_init_mpi.c"])
cc.link(
    "scorep_init_mpi",
    objects=["./scorep_init_mpi.o"],
    output_filename=mpi_lib_name,
    library_dirs=lib_dir_mpi,
    extra_postargs=linker_flags_mpi)

mpi_link_name = scorep.helper.gen_mpi_link_name()

linker_flags_mpi.append("-l{}".format(mpi_link_name))

module1 = Extension('scorep.scorep_bindings',
                    include_dirs=include,
                    libraries=[],
                    library_dirs=lib_dir,
                    define_macros=macro,
                    extra_link_args=linker_flags,
                    extra_compile_args=["-std=c++11"],
                    sources=['src/scorep.cpp', 'scorep_init.c'])

module2 = Extension('scorep.scorep_bindings_mpi',
                    include_dirs=include_mpi,
                    libraries=[],
                    library_dirs=lib_dir_mpi + ["./"],
                    define_macros=macro_mpi + [("USE_MPI", None)],
                    extra_link_args=linker_flags_mpi,
                    extra_compile_args=["-std=c++11"],
                    sources=['src/scorep.cpp'])

setup(
    name='scorep',
    version='0.7',
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
    packages = ['scorep'],
    data_files=[("lib", [mpi_lib_name])],
    ext_modules=[module1, module2]
)
