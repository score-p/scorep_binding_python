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
Allows to change the installation target. To use the module the path ```<location>``` has to be in the ```PYTHONPATH```

# Use

To trace the full script you need to run

```
python -m scorep <script.py>
```

Alternatively you can kick of the tracing from insed your script by using:

```
import scorep
t = scorep.Trace(True)
t.register()
```

Then all code after the call to `t.register()` is traced. This might be helpfull to avoid tracing the inialisation of some imported modules.

Moreover, you can trace masterprocesses that usees python multiprocessing.
Please be aware, that the current version of scorep does not support tracing of the by multiprocessing forked processes.   

The usual Score-P environment Variables will be respected. Please have a look at:

[www.vi-hps.org](http://www.vi-hps.org/projects/score-p/)

and

[Score-P Documentation](https://silc.zih.tu-dresden.de/scorep-current/pdf/scorep.pdf)

# Compatibility
The installation script works with python3 and python2.

# User instrumentation

In some cases the user might want to define a region, log some parameters, or just diable tracing for a certaing areat. To do so the module implements a few functions:

```
scorep.user_region_begin(name)
scorep.user_region_end(name)
```

These functions allow the definition of user regions. `name` defines the name of a region. Each `user_region_begin` shall have a coresponding call to `user_region_end`.    


```
scorep.user_enable_recording()
scorep.user_disable_recording()
```

These functiontons alow enabling and disabling of the tracing.

```
scorep.user_parameter_int(name, val)
scorep.user_parameter_uint(name, val)
scorep.user_parameter_string(name, string)
```

These functions allow to pass user parameters to scorep. These parameters can be int, uint and string. `name` defines the name of the parameter, while `val` or `string` defines the value that is passed to Score-P. 

# Tracing
The tracing uses Score-P User instrumentation. The python trace module was reworked, to pass the region names to ```SCOREP_USER_REGION_BY_NAME_BEGIN(name,type)``` and ```SCOREP_USER_REGION_BY_NAME_END(name)``` instead of printing. All other features of the tracing module where striped.
