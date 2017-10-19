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

"""
return a triple with (returncode, stdout, stderr) from the call to subprocess
"""
def call(arguments):
    result = ()
    if sys.version_info > (3,5):
        out = subprocess.run(arguments,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        result = (out.returncode, out.stdout.decode("utf-8"), out.stderr.decode("utf-8"))
    else:
        p = subprocess.Popen(arguments,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        p.wait()
        result = (p.returncode,stdout.decode("utf-8"), stderr.decode("utf-8"))
    return result
         

scorep_config = ["scorep-config","--nocompiler", "--user", "--thread=pthread", "--mpp=none"]
scorep_config_mpi = ["scorep-config","--nocompiler", "--user", "--thread=pthread", "--mpp=mpi"]

def get_config(scorep_config):
    (retrun_code, _ ,_) = call(scorep_config + ["--cuda"])
    if retrun_code == 0:
        scorep_config.append("--cuda")
        print("Cuda is supported, building with cuda")
    else:
        print("Cuda is not supported, building without cuda")
        scorep_config.append("--nocuda")
        
    (retrun_code, _ ,_) = call(scorep_config + ["--opencl"])
    if retrun_code == 0:
        scorep_config.append("--opencl")
        print("OpenCL is supported, building with OpenCL")
    else:
        print("OpenCl is not supported, building without OpenCL")
        scorep_config.append("--noopencl")
                  
    
    (_, ldflags, _) = call(scorep_config + ["--ldflags"])
    (_, libs, _)    = call(scorep_config + ["--libs"])
    (_, mgmt_libs, _)    = call(scorep_config + ["--mgmt-libs"])
    (_, cflags, _)  = call(scorep_config + ["--cflags"])
     
    (_, scorep_adapter_init, _) = call(scorep_config + ["--adapter-init"])
     
    libs = libs + " " + mgmt_libs

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

def get_mpi_config():
    (_,mpi_version, mpi_version2) = call(["mpiexec", "--version"])
    mpi_version = mpi_version + mpi_version2
    if "OpenRTE" in mpi_version:
        print("OpenMPI detected")
        (_,ldflags,_) = call(["mpicc", "-showme:link"])
        (_,compile_flags,_) = call(["mpicc", "-showme:compile"])
    elif ("Intel" in mpi_version) or ("MPICH" in mpi_version):
        print("Intel or MPICH detected")
        (_,ldflags,_) = call(["mpicc", "-link_info"])
        (_,compile_flags,_) = call(["mpicc", "-compile_info"])
    else:
        print("cannot determine mpi version: \"{}\"".format(mpi_version))
        exit(-1)
    
    print(ldflags)
    lib_dir = re.findall("-L[/+-@.\w]*",ldflags)
    lib     = re.findall("-l[/+-@.\w]*",ldflags)
    include = re.findall("-I[/+-@.\w]*",compile_flags)
    macro   = re.findall("-D[/+-@.\w]*",compile_flags)
    linker_flags = re.findall("-Wl[/+-@.\w]*",ldflags)
    linker_flags_2 = re.findall("-Xlinker [/+-@.\w]*",ldflags)
    
    
    remove_flag3 = lambda x: x[2:]
    remove_x_linker = lambda x: x[9:]
    remove_space1 = lambda x: x[0:]
    
    lib_dir      = list(map(remove_flag3, lib_dir))
    lib          = list(map(remove_flag3, lib))
    include      = list(map(remove_flag3, include))
    macro        = list(map(remove_flag3, macro))
    linker_flags = list(map(remove_space1, linker_flags)) 
    linker_flags_2 = list(map(remove_x_linker, linker_flags))
    
    macro   = list(map(lambda x: tuple([x,1]), macro))
    
    linker_flags.extend(linker_flags_2)
    
    return (include, lib, lib_dir, macro, linker_flags)

(include, lib, lib_dir, macro, linker_flags, scorep_adapter_init) = get_config(scorep_config)
(include_mpi, lib_mpi, lib_dir_mpi, macro_mpi, linker_flags_mpi, scorep_adapter_init_mpi) = get_config(scorep_config_mpi)
(include_mpi_, lib_mpi_, lib_dir_mpi_, macro_mpi_, linker_flags_mpi_) = get_mpi_config()

include_mpi.extend(include_mpi_)
lib_mpi.extend(lib_mpi_)
lib_dir_mpi.extend(lib_dir_mpi_)
macro_mpi.extend(macro_mpi_)
linker_flags_mpi.extend(linker_flags_mpi_)

print(lib_dir_mpi)

with open("./scorep_init.c","w") as f:
    f.write(scorep_adapter_init)
    
with open("./scorep_init_mpi.c","w") as f:
    f.write(scorep_adapter_init_mpi)

## black magic to find prefix
# Setup the default install prefix
prefix = sys.prefix

# Get the install prefix if one is specified from the command line
for arg in sys.argv:
    if arg.startswith('--prefix='):
        prefix = arg[9:]
        prefix = os.path.expandvars(prefix)


# build scorep with mpi for ld_prealod
cc = distutils.ccompiler.new_compiler()
cc.compile(["./scorep_init_mpi.c"])
cc.link("scorep_init_mpi",objects = ["./scorep_init_mpi.o"],output_filename = "./libscorep_init_mpi.so",\
        library_dirs = lib_dir_mpi, libraries = lib_mpi)

module1 = Extension('_scorep',
                    include_dirs = include,
                    libraries = lib,
                    library_dirs = lib_dir,
                    define_macros = macro,
                    extra_link_args = linker_flags,
                    sources = ['scorep.c','scorep_init.c'])

module2 = Extension('_scorep_mpi',
                    include_dirs = include_mpi,
                    libraries = lib_mpi + ["scorep_init_mpi"],
                    library_dirs = lib_dir_mpi + ["./"],
                    runtime_library_dirs = ["{}/lib/".format(prefix)],
                    define_macros = macro_mpi + [("USE_MPI",None)],
                    extra_link_args = linker_flags_mpi, 
                    sources = ['scorep.c'])


## modify scorep.py for a shebang with the right python version
# fix python interpreter 
# from https://stackoverflow.com/a/17099342
def fix_shebang(file_path, python_version):
    """Rewrite the  shebang for the used major python version of the install,
    use simply sed from OS"""
    print("fix python version")
    # accept array of python version from platform.python_version_tuple()
    # fix shebang only with major python version
    sed = "sed -i 's/#!.*\/usr\/bin\/.*python.*$/#!\/usr\/bin\/env python{}/'"\
            .format(python_version[0], python_version[1])
    # bring command together with file path
    cmd = ' '.join([sed, file_path])
    # execute the sed command and replace in place
    os.system(cmd)

# Get current Python version
fix_shebang_curr = functools.partial(fix_shebang, python_version=platform.python_version_tuple())

# add execution rights to file
def add_exec(file_path):
    """Add execution rights for user, group and others to the given file"""

    print("change permissions")
    # change Permission with bitwies or and the constants from stat modul
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR|  stat.S_IXUSR | \
            stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

# global vars are very bad but I think the only solution for this
all_data_files = None

# fix the path of an installed file in another file
def fix_path(file_path, fix_file_name):
    """Setting the correct path in the given file with the matching file from
    the list of all files from own install_data, use simply sed from OS"""
    
    global all_data_files

    print("change path for " + fix_file_name)
    # find matching pathes in the list with the installed files
    matching_files = list(filter(lambda x: fix_file_name in x, all_data_files))

    if len(matching_files) == 0:
        print("no matching files were installed, do nothing")
        return
    elif len(matching_files) > 1:
        print("multiple files were found, make name more precise")
        return
    new_path = os.path.abspath(matching_files[0])

    # replace all absolute paths that contains the given file name with an
    # arbitrary filetyp postfix and surrounded by " or not
    sed = "sed -i 's:\"*\(/.*\)*/{}\..*\"*:\"{}\":g'".format(fix_file_name, new_path)
    # bring command together with file path
    cmd = ' '.join([sed, file_path])
    # execute the sed command and replace in place
    os.system(cmd)
    
fix_init_mpi = functools.partial(fix_path, fix_file_name="libscorep_init_mpi") 

# custom class for additional install_data instructions
class my_install_data(install_data):

    def run(self):
        # standard install_data routine
        install_data.run(self)
        # get all installed data files
        global all_data_files
        all_data_files = self.get_outputs()

# custom class for additional install instructions
class my_install(install):
    # Dict with a filename and the function that should be executed 
    # upon the matching files
    # function must have only one parameter, the file path
    files_and_commands = {'scorep.py' : (add_exec, fix_shebang_curr, fix_init_mpi)}

    def run(self):
        # standard install routine
        install.run(self)
        # get all installed files
        install_files = self.get_outputs()

        ## Parse dictionary
        # first loop over all key of the dict
        for key in self.files_and_commands.keys():
            # find matching pathes in the list with the installed files
            matching_files = list(filter(lambda x: key in x, install_files))
            # loop over all matching files
            for files in matching_files:
                # and over the file operations
                for function in self.files_and_commands[key]:
                    # apply file operations
                    function(files)

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
    py_modules = ['scorep'],
    data_files = [("lib",["libscorep_init_mpi.so"])],
    ext_modules = [module1,module2],
    cmdclass={'install': my_install, 'install_data': my_install_data}
)

