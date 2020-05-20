[![Build Status](https://travis-ci.com/score-p/scorep_binding_python.svg?branch=master)](https://travis-ci.com/score-p/scorep_binding_python)
[![Unit tests](https://github.com/score-p/scorep_binding_python/workflows/Unit%20tests/badge.svg?branch=master)](https://github.com/score-p/scorep_binding_python/actions?query=workflow%3A"Unit+tests")
[![Static analysis](https://github.com/score-p/scorep_binding_python/workflows/Static%20analysis/badge.svg?branch=master)](https://github.com/score-p/scorep_binding_python/actions?query=workflow%3A"Static+analysis")

# scorep
scorep is a module that allows tracing of python scripts using [Score-P](http://www.vi-hps.org/projects/score-p/).

# Table of Content

- [scorep](#scorep)
- [Table of Content](#table-of-content)
- [Install](#install)
- [Use](#use)
  * [Instrumenter](#instrumenter)
    + [Instrumenter Types](#instrumenter-types)
    + [Instrumenter User Interface](#instrumenter-user-interface)
  * [MPI](#mpi)
  * [User Regions](#user-regions)
  * [Overview about Flags](#overview-about-flags)
  * [Backward Compatibility](#backward-compatibility)
- [Compatibility](#compatibility)
  * [Working](#working)
  * [Not Working](#not-working)
- [Acknowledgments](#acknowledgments)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

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

## Instrumenter
The instrumenter ist the key part of the bindings.
He registers with the Python tracing interface, and cares about the fowarding of events to Score-P.
There are currently three different instrumenter types available as described in the following section [Instrumenter Types](#instrumenter-types) .
A user interface, to dynamically enable and disable the automatic instrumentation, using the python hooks, is also available and described under [Instrumenter User Interface](#instrumenter-user-interface)

### Instrumenter Types
With version 2.0 of the python bindings, the term "instrumenter" is introduced. The instrumenter describes the class that maps the Python `trace` or `profile` events to Score-P. Please be aware, that `trace` and `profile` does not refer to the traditional Score-P terms of tracing and profiling, but to the Python functions [sys.settrace](https://docs.python.org/3/library/sys.html#sys.settrace) and [sys.setprofile](https://docs.python.org/3/library/sys.html#sys.setprofile).

The instrumenter that shall be used for tracing can be specified using `--instrumenter-type=<type>`.
Currently there are the following tacers available:
 * `profile` (default) implements `call` and `return`  
 * `trace` implements `call` and `return`
 * `dummy` does nothing, can be used without `-m scorep` (as done by user instrumentation)

The `profile` instrumenter should have a smaller overhead than `trace`.

It is possible to disable the instrumenter passing  `--noinstrumenter`.
However, the [Instrumenter User Interface](#instrumenter-user-interface) may override this flag.

### Instrumenter User Interface

It is possible to enable or disable the instrumenter during the program runtime using a user interface:

```
with scorep.instrumenter.disable():
    do_something()

with scorep.instrumenter.enable():
    do_something()    
```

The main idea is to reduce the instrumentation overhead for regions that are not of interest.
Whenever the instrumenter is disabled, function enter or exits will not be trace.
However, user regions as described in [User Regions](#user-regions) are not affected.

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

With version 3.1 the bindings support the annotation of regions where the instrumenter setting was changed.
You can pass a `region_name` to the instrumenter calls, e.g. `scorep.instrumenter.enable("enabled_region_name")` or `scorep.instrumenter.disable("disabled_region_name")`.
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

However, doing 
```
[...]
with scorep.instrumenter.disable():
    with scorep.instrumenter.disable("my_fun_calls"):
        fun_calls(1000000)
[...]
```
will only disable the instrumenter, but `my_fun_calls` will not appear in the trace or profile, as the second call to `scorep.instrumenter.disable` did not change the state of the instrumenter.
Please look to [User Regions](#user-regions), if you want to annotate a region, no matter what the instrumenter state is.

## MPI

To use trace an MPI parallel application, please specify

```
python -m scorep --mpp=mpi <script.py>
```

## User Regions
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
