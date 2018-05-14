# How to use trace a python application using Score-P

Score-P itself is a really powerfull tool to understand an application and to analyse the perfromance of an applicatioon.
It is desinged to understand highly parralell applications, as they typically found in the Area of High Perfmance Computing.
However, using the provided Python Bindings it allows also the tracing and understanding the perfromance of python applications.

This HowTo will give you a short introduction how to set up Score-P, how to Trace, and how to view the results using CUBE and Vampir. [link]

## Download And Install

#### Score-P

First you need to download and install Score-P. On a typically debian based System you simply need to tpye the following in your shell:

```
wget http://www.vi-hps.org/upload/packages/scorep/scorep-4.0.tar.gz
tar -xf scorep-4.0.tar.gz
cd scorep-4.0/
mkdir build
cd build
../configure
make 
sudo make install
```

This will install Score-P into the typical locations on your System.

You can change the install location by specifying

```
../configure --prefix=/some/location/
```

However, please be sure to set the `$LD_LIBRARY_PATH` and `$PATH` adequately.

#### Cube

To visualise the profile you might need CUBE. To install please do:

```
wget http://apps.fz-juelich.de/scalasca/releases/cube/4.4/dist/cubegui-4.4.tar.gz
tar -xf cubegui-4.4.tar.gz
cd cubegui-4.4
mkdir build
cd build
../configure
make 
sudo make install
```

This will install Cube into the typical locations on your System.

You can change the install location by specifying

```
../configure --prefix=/some/location/
```

However, please be sure to set the `$LD_LIBRARY_PATH` and `$PATH` adequately.


#### Installing the Score-P Python bindings

To install the python bindings you simply need to clone the repository, and install it using pip:

```
git clone https://github.com/score-p/scorep_binding_python
cd scorep_python_bindings/
pip3 install .
```

The bindings are supposed to be python 2.7 compatible. However, I really recommend to use python 3.5 upwards.


## Profile and Trace an Application

As traces might get really large it is recommended to first profile you application, and to create a filter file.
For some use cases profiling might even be sufficient.

### Invoke Score-P

First you need to profile your application using the python bindings you have just installed. To do so simply let the scorep python module execute your Application:

```
python3 -m scorep yout_app.py
```

From the test sets you can for example use the test_sleep.py:

```
cd test/
python3 -m scorep test_sleep.py
```

This will create a Folder in the sam directory, which is named like:

```
scorep-20180514_1012_10320848076853/
```

You might have realised that the current day as well as the time at, which you run the experiment is encoded in this name. You can change the name of the directory by specifying `SCOREP_EXPERIMENT_DIRECTORY`:

```
export SCOREP_EXPERIMENT_DIRECTORY=test_dir
python3 -m scorep test_sleep.py
```

This will create a directory called `test_dir`

### Show the Profile.

The folder, which you just created contains now different files like:

```
profile.cubex
scorep.cfg
scorep.fgp
```

The profile is saved in `profile.cubex`. If you have cube installed you can do:

```
cube test_dir/profile.cubex
```

This will show you the following picture:

