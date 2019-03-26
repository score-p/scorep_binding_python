# scorep
scorep is a module that allows tracing of python scripts using [Score-P](http://www.vi-hps.org/projects/score-p/).

# Install
You need at least Score-P 5.0, build with `--enable-shared`.
Please make sure, that `scorep-config` is in your `PATH` variable.

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

Since version 0.9 it is possible to pass the traditional Score-P commands to the Score-P bindings, e.g.:

```
python -m scorep --mpp=mpi --thread=pthread <script.py>
```

To see all flags simply call:

```
scorep --help
```

## MPI

To use trace an MPI parallel application, please specify

```
python -m scorep --mpp=mpi <script.py>
```

## User instrumentation

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
Please be aware, that the scorep module still needs to be preloaded, i.e. by using `python -m scorep`.

## Additional Flags

The Score-P bindings now also support a `--nopython` flag, which disables the python instrumentation.
This might be helpful, if only user instrumentation is required, or only some instrumented libraries shall be traced.

## Backward Compatibility

In order to maintain backwards Compatibility, the following flags are set per default:

```
python -m scorep --compiler --thread=pthread <script.py>
```

The traditional `--mpi` does still work, and is similar to the following call:

```
python -m scorep --compiler --thread=pthread --mpp=mpi <script.py>
```

To disable compiler instrumentation please specify:

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
    * Score-P does currently not support any non MPI or non SHMEM communication. So the different processes will not know from each other. You might want to take a look to https://mpi4py.readthedocs.io/en/stable/mpi4py.futures.html .

# Tracing
The tracing uses Score-P User instrumentation. The python trace module was reworked, to pass the region names to `SCOREP_USER_REGION_BEGIN` and `SCOREP_USER_REGION_END` instead of printing. All other features of the tracing module where striped.
