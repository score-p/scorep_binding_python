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
import os
import subprocess
import re
import sys

"""
return a tuple with (returncode,stdout) from the call to subprocess
"""
def call(arguments):
    result = ()
    if sys.version_info > (3,5):
        out = subprocess.run(arguments,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        result = (out.returncode, out.stdout.decode("utf-8"))
    else:
        p = subprocess.Popen(arguments,stdout=subprocess.PIPE,stderr=None)
        stdout, _ = p.communicate()
        p.wait()
        result = (p.returncode,stdout)
    return result
         

scorep_config = ["scorep-config","--nocompiler", "--user", "--thread=pthread", "--mpp=none"]
scorep_config_mpi = ["scorep-config","--nocompiler", "--user", "--thread=pthread", "--mpp=mpi"]

def get_config(scorep_config):
    (retrun_code, _) = call(scorep_config + ["--cuda"])
    if retrun_code == 0:
        scorep_config.append("--cuda")
        print("Cuda is supported, building with cuda")
    else:
        print("Cuda is not supported, building without cuda")
        scorep_config.append("--nocuda")
        
    (retrun_code, _) = call(scorep_config + ["--opencl"])
    if retrun_code == 0:
        scorep_config.append("--opencl")
        print("OpenCL is supported, building with OpenCL")
    else:
        print("OpenCl is not supported, building without OpenCL")
        scorep_config.append("--noopencl")
                  
    
    (_, ldflags) = call(scorep_config + ["--ldflags"])
    (_, libs)    = call(scorep_config + ["--libs"])
    (_, cflags)  = call(scorep_config + ["--cflags"])
     
    (_, scorep_adapter_init) = call(scorep_config + ["--mpp=none", "--adapter-init"])
     
    lib_dir = re.findall(" -L[/+-@.\w]*",ldflags)
    lib     = re.findall(" -l[/+-@.\w]*",libs)
    include = re.findall(" -I[/+-@.\w]*",cflags)
    macro   = re.findall(" -D[/+-@.\w]*",cflags)
    linker_flags = re.findall(" -Wl[/+-@.\w]*",ldflags)
    
    remove_flag3 = lambda x: x[3:]
    remove_space1 = lambda x: x[1:]
    
    lib_dir      = list(map(remove_flag3, lib_dir))
    lib          = list(map(remove_flag3, lib))
    include      = list(map(remove_flag3, include))
    macro        = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags)) 
    
    macro   = list(map(lambda x: tuple([x,1]), macro))
    
    return (include, lib, lib_dir, macro, linker_flags, scorep_adapter_init)

(include, lib, lib_dir, macro, linker_flags, scorep_adapter_init) = get_config(scorep_config)
(include_mpi, lib_mpi, lib_dir_mpi, macro_mpi, linker_flags_mpi, scorep_adapter_init_mpi) = get_config(scorep_config_mpi)

with open("./scorep_init.c","w") as f:
    f.write(scorep_adapter_init)
    
with open("./scorep_init_mpi.c","w") as f:
    f.write(scorep_adapter_init_mpi)


module1 = Extension('scorep',
                    include_dirs = include,
                    libraries = lib,
                    library_dirs = lib_dir,
                    define_macros = macro,
                    extra_link_args = linker_flags, 
                    sources = ['scorep.c',"scorep_init.c"])

module2 = Extension('scorep_mpi',
                    include_dirs = include_mpi,
                    libraries = lib_mpi,
                    library_dirs = lib_dir_mpi,
                    define_macros = macro_mpi + [("USE_MPI",None)],
                    extra_link_args = linker_flags_mpi, 
                    sources = ['scorep.c',"scorep_init_mpi.c"])


setup (
    name = 'scorep',
    version = '0.5',
    description = 'This is a scorep tracing package',
    author = 'Andreas Gocht',
    author_email = 'andreas.gocht@tu-dresden.de',
    url = '',
    long_description = '''
This package allows taring of python code using Score-P]

The Package just uses Score-P user regions.

Differnend python theads are not differentiated, but using MPI should work (not tested).

This module is more or less similar to the python trace module. 
''',
    py_modules = ['scorep_trace'],
    ext_modules = [module1,module2])
