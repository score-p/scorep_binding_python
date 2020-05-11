[![Build Status](https://travis-ci.com/score-p/scorep_binding_python.svg?branch=master)](https://travis-ci.com/score-p/scorep_binding_python)

# scorep
scorep is a module that allows tracing of python scripts using [Score-P](http://www.vi-hps.org/projects/score-p/).

# Install
You need at least Score-P 5.0, build with `--enable-shared` and the gcc compiler plugin.
Please make sure that `scorep-config` is in your `PATH` variable.

For Ubuntu LTS systems there is a non-official ppa of Score-P available: https://launchpad.net/~andreasgocht/+archive/ubuntu/scorep .

Then run

```
pip install .
```
# Use

To trace the full script, you need to run

```
python -m scorep <script.py>
```

The usual Score-P environment Variables will be respected. Please have a look at:

[www.vi-hps.org](http://www.vi-hps.org/projects/score-p/)

and

[Score-P Documentation](http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/docs/latest/pdf/scorep.pdf)

There is also a small [HowTo](https://github.com/score-p/scorep_binding_python/wiki) in the wiki.

Since version 0.9 it is possible to pass the traditional Score-P commands to the Score-P bindings, e.g.:

```
python -m scorep --mpp=mpi --thread=pthread <script.py>
```

## MPI

To use trace an MPI parallel application, please specify

```
python -m scorep --mpp=mpi <script.py>
```

## User instrumentation
### User Regions
Since version 2.0 the python bindings support context managers for user regions:

```
with scorep.user.region("region_name"):
    do_something()
```

Since version 2.1 the python bindings support also decorators for functions:

```
@scorep.user.region("region_name")
def do_something():
    #do some things
```
If no region name is given, the function name will be used e.g.:

```
@scorep.user.region()
def do_something():
    #do some things
```

will result in `__main__:do_something`.

The traditional calls to define a region still exists, but the usage is discouraged:

```
scorep.user.region_begin("region_name")
scorep.user.region_end("region_name")
```

User parameters can be used in any case:

```
scorep.user.parameter_int(name, val)
scorep.user.parameter_uint(name, val)
scorep.user.parameter_string(name, string)
```

where `name` defines the name of the parameter or region, while `val` or `string` represents the value that is passed to Score-P. 

Disabeling the recording with Score-P is still also possilbe:

```
scorep.user.enable_recording()
scorep.user.disable_recording()
```

However, please be aware that the runtime impact of disabeling Score-P is rather small, as the instrumenter is still active. For details about the instrumenter, please see [Instrumenter](#Instrumenter).  

### Instrumenter
With version 2.0 of the python bindings, the term "instrumenter" is introduced. The instrumenter describes the class that maps the Python `trace` or `profile` events to Score-P. Please be aware, that `trace` and `profile` does not refer to the traditional Score-P terms of tracing and profiling, but to the Python functions [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) and [sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile).

The instrumenter that shall be used for tracing can be specified using `--instrumenter-type=<type>`.
Currently there are the following tacers available:
 * `profile` (default) implements `call` and `return`  
 * `trace` implements `call` and `return`
 * `dummy` does nothing, can be used without `-m scorep` (as done by user instrumentation)

The `profile` instrumenter should have a smaller overhead than `trace`. 

Moreover it is possible to disable (and enable) the instrumenter in the sourcecode:

```
with scorep.instrumenter.disable():
    do_something()

with scorep.instrumenter.enable():
    do_something()    
```

or during startup with `--noinstrumenter`. The given function calls override this flag.

The main idea is to reduce the instrumentation overhead for regions that are not of interest.
Whenever the instrumenter is disabled, function enter or exits will not be trace.

As an example:

```
import numpy as np

[...]
c = np.dot(a,b)
[...]
```

You might not be interested, what happens during the import of numpy, but actually how long `dot` takes.
If you change the code to

```
import numpy as np
import scorep

[...]
with scorep.instrumenter.enable():
    c = np.dot(a,b)
[...]
```
and run the code with `python -m scorep --noinstrumenter run.py` only the call to np.dot and everything below will be instrumented.
Please be aware, that user instrumentation, using scorep.user will always be recorded.


With version 3.1 the bindings support the annotation of regions where the instrumenter was explicit enabled or disabled.
You can now pass a `region_name` to `scorep.instrumenter.enable("enabled_region_name")` and `scorep.instrumenter.disable("disabled_region_name")`.
This might be useful if you do something expensive, and just want to know how long it takes, but you do not care what happens exactly e.g.:

```
[...]
def fun_calls(n):
    if (n>0):
        fun_calls(n-1)

with scorep.instrumenter.disable("my_fun_calls"):
    fun_calls(1000000)
[...]
```

`my_fun_calls` will be present in the trace or profile but `fun_calls` will not.

## Overview about Flags

The following flags are special to the python bindings:

 * `--noinstrumenter` disables the instrumentation of python code. Usefull for user instrumentation and to trace only specific code regions using `scorep.instrumenter.enable`.
 * `--instrumenter-type=<type>` choose an instrumenter. See  [Instrumenter](#Instrumenter).
 * `--keep-files` temporary files are kept.

## Backward Compatibility

To maintain backwards compatibility, the following flags are set per default:

```
python -m scorep --compiler --thread=pthread <script.py>
```

The traditional `--mpi` does still work, and is similar to the following call:

```
python -m scorep --compiler --thread=pthread --mpp=mpi <script.py>
```

To disable compiler instrumentation, please specify:

```
python -m scorep --nocompiler <script.py>
```

For other thread schemes just specify `--thread=<something>`. E.g. :

```
python -m scorep --thread=omp <script.py>
```

Please be aware the `--user` is always passed to Score-P, as this is needed for the python instrumentation.

# Compatibility
## Working
* python3 
* python2.7
* mpi using mpi4py
* threaded applications


## Not Working
* python multiprocessing
    * Score-P does currently only support MPI or SHMEM. Any other multiprocessing approach cannot be traced.
    
# Acknowledgments
The European Union initially supported this work as part of the European Union’s Horizon 2020 project READEX (grant agreement number 671657).
