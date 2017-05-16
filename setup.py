from distutils.core import setup, Extension
import os
import subprocess
import re
import sys 


    
scorep_config = ["scorep-config","--nocompiler", "--user"]

if subprocess.run(scorep_config + ["--cuda"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
    scorep_config.append("--cuda")
    print("Cuda is supported, building with cuda")
else:
    print("Cuda is not supported, building without cuda")
    
              

ldflage =   subprocess.run(scorep_config + ["--ldflags"], stdout=subprocess.PIPE).stdout
libs =      subprocess.run(scorep_config + ["--libs"], stdout=subprocess.PIPE).stdout
cflags =    subprocess.run(scorep_config + ["--cflags"], stdout=subprocess.PIPE).stdout
 
scorep_adapter_init = subprocess.run(scorep_config + ["--adapter-init"], stdout=subprocess.PIPE).stdout
 
libs        = libs.decode("utf-8")
ldflage     = ldflage.decode("utf-8")
cflags      = cflags.decode("utf-8")

scorep_adapter_init = scorep_adapter_init.decode("utf-8")

lib_dir = re.findall("-L[/.\w]*",ldflage)
lib     = re.findall("-l[/.\w]*",libs)
include = re.findall("-I[/.\w]*",cflags)
macro   = re.findall("-D[/.\w]*",cflags)

remove_flag = lambda x: x[2:]

lib_dir = list(map(remove_flag, lib_dir))
lib     = list(map(remove_flag, lib))
include = list(map(remove_flag, include))
macro   = list(map(remove_flag, macro))

macro   = list(map(lambda x: tuple([x,1]), macro))

    

with open("./scorep_init.c","w") as f:
    f.write(scorep_adapter_init)

module1 = Extension('scorep',
                    include_dirs = include,
                    libraries = lib,
                    library_dirs = lib_dir,
                    define_macros = macro,
                    sources = ['scorep.c',"scorep_init.c"])


setup (
    name = 'scorep',
    version = '0.3',
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
    ext_modules = [module1])
