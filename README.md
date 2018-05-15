# scorep
scorep is a module that allows tracing of python scripts using [Score-P](http://www.vi-hps.org/projects/score-p/).

# Install
You need to have scorep-config in your ```PATH``` variable.

Then simply run
```
python setup.py install
```

The option
```
--prefix=<location>
```
Allows changing the installation target. To use the module the path ```<location>``` has to be in the ```PYTHONPATH```

# Use

To trace the full script you need to run

```
python -m scorep <script.py>
```

Alternatively, you can kick of the tracing from inside your script by using:

```
import scorep
scorep.register()
```

Then all code after the call to `scorep.register()` is traced. This might be helpful to avoid tracing the initialisation of some imported modules.

The usual Score-P environment Variables will be respected. Please have a look at:

[www.vi-hps.org](http://www.vi-hps.org/projects/score-p/)

and

[Score-P Documentation](https://silc.zih.tu-dresden.de/scorep-current/pdf/scorep.pdf)

# Compatibility
## Working
* python3 
* python2

## Not Working

## Partialy working
* threaded applications
    * Please have a look to a Score-P trunk package with revision at least 13560 here:
      http://scorepci.pages.jsc.fz-juelich.de/scorep-pipelines/.
* python multiprocessing
    * Please have a look to [multiprocessing](#multiprocessing).

# multiprocessing
Tracing the python multiprocessing is a bit ugly currently. Score-P does currently not support any non MPI or non SHMEM communication. So the different processes will not know from each other.

However, you can trace master-processes. To do so you must need to do:

```
import scorep
scorep.register()
```

Using the ```python -m scorep <script.py>``` won't work (but the python tracing doesn't work in this case either.). 

To trace the sub-processes created by the master-processes might work, but is **not** supported.

You need to do the following:

```
import os
os.environ["SCOREP_EXPERIMENT_DIRECTORY"] = "/some/dir/with/<process_num>"
import scorep
scorep.register()
```

How you determine the process_num is up to you. You will end up with different traces for each process.
    
# User instrumentation

In some cases, the user might want to define a region, log some parameters, or just disable tracing for a certain area. To do so the module implements a few functions:

```
scorep.user_region_begin(name)
scorep.user_region_end(name)
```

These functions allow the definition of user regions. `name` defines the name of a region. Each `user_region_begin` shall have a corresponding call to `user_region_end`.    


```
scorep.user_enable_recording()
scorep.user_disable_recording()
```

These functions allow enabling and disabling of the tracing.

```
scorep.user_parameter_int(name, val)
scorep.user_parameter_uint(name, val)
scorep.user_parameter_string(name, string)
```

These functions allow passing user parameters to Score-P. These parameters can be int, uint and string. `name` defines the name of the parameter, while `val` or `string` defines the value that is passed to Score-P. 

# Tracing
The tracing uses Score-P User instrumentation. The python trace module was reworked, to pass the region names to ```SCOREP_USER_REGION_BY_NAME_BEGIN(name,type)``` and ```SCOREP_USER_REGION_BY_NAME_END(name)``` instead of printing. All other features of the tracing module where striped.

# MPI


This version of the Score-P python tracing plugin supports MPI. To use it please specify `--mpi`:

```
python -m scorep --mpi <script.py>
```

This will ensure, that the right Score-P libs are in `LD_PRELOAD`. It will re-execute the tracing script, with the preloaded libs.
