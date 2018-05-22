# scorep
scorep is a module that allows tracing of python scripts using [Score-P](http://www.vi-hps.org/projects/score-p/).

# Install
You need to have scorep-config in your `PATH` variable.

Then simply run
```
pip install .
```
# Use

To trace the full script you need to run

```
python -m scorep <script.py>
```

The usual Score-P environment Variables will be respected. Please have a look at:

[www.vi-hps.org](http://www.vi-hps.org/projects/score-p/)

and

[Score-P Documentation](https://silc.zih.tu-dresden.de/scorep-current/pdf/scorep.pdf)

There is also a small [HowTo](https://github.com/score-p/scorep_binding_python/wiki) in the wiki.

# Compatibility
## Working
* python3 
* python2.7
* mpi using mpi4py

## Not Working
* python multiprocessing
    * Score-P does currently not support any non MPI or non SHMEM communication. So the different processes will not know from each other. You might want to take a look to https://mpi4py.readthedocs.io/en/stable/mpi4py.futures.html .

## Partialy working
* threaded applications
    * Please have a look to a Score-P trunk package with revision at least 13560 here:
      http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/.
    
# User instrumentation

In some cases, the user might want to define a region, log some parameters, or just disable tracing for a certain area. To do so the module implements a few functions:

```
scorep.user.region_begin(name)
scorep.user.region_end(name)
```

These functions allow the definition of user regions. `name` defines the name of a region. Each `user.region_begin` shall have a corresponding call to `user.region_end`.    


```
scorep.user.enable_recording()
scorep.user.disable_recording()
```

These functions allow enabling and disabling of the tracing.

```
scorep.user.parameter_int(name, val)
scorep.user.parameter_uint(name, val)
scorep.user.parameter_string(name, string)
```

These functions allow passing user parameters to Score-P. These parameters can be int, uint and string. `name` defines the name of the parameter, while `val` or `string` defines the value that is passed to Score-P. 

# Tracing
The tracing uses Score-P User instrumentation. The python trace module was reworked, to pass the region names to ```SCOREP_USER_REGION_BEGIN``` and ```SCOREP_USER_REGION_END``` instead of printing. All other features of the tracing module where striped.

# MPI

This version of the Score-P python tracing plugin supports MPI. To use it please specify `--mpi`:

```
python -m scorep --mpi <script.py>
```

This will ensure, that the right Score-P libs are in `LD_PRELOAD`. It will re-execute the tracing script, with the preloaded libs.
