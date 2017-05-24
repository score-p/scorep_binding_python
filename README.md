# scorep_python
scorep_python is a module that allows tracing of python scripts using scorep.

# Install
You need to have scorep-config in your ```PATH``` variable.

Then simply run
```
python3 setup.py install
```

The option
```
--prefix=<location>
```
Allows to change the installation target. To use the module the path ```<location>``` has to be in the ```PYTHONPATH```

# Use

To trace the full script you need to run

```
python3 -m scorep_trace <script.py>
```

Alternatively you can kick of the tracing from insed your script by using:

```
import scorep_trace
t = scorep_trace.Trace(True)
t.register()
```

Then all code after the call to `t.register()` is traced. This might be helpfull to avoid tracing the inialisation of some imported modules.

Moreover, you can trace masterprocesses that usees python multiprocessing.
Please be aware, that the current version of scorep_trace does not support tracing of the by multiprocessing forked processes.   

The usual Score-P environment Variables will be respected. Please have a look at:

[www.vi-hps.org](http://www.vi-hps.org/projects/score-p/)

and

[Score-P Documentation](https://silc.zih.tu-dresden.de/scorep-current/pdf/scorep.pdf)

# Compatibility
The installation script works with python3. Python2 is not tested.

# Tracing
The tracing uses Score-P User instrumentation. The python trace module was reworked, to pass the region names to ```SCOREP_USER_REGION_BY_NAME_BEGIN(name,type)``` and ```SCOREP_USER_REGION_BY_NAME_END(name)``` instead of printing. All other features of the tracing module where striped.
