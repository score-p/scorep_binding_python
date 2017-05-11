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

To trace the a script you need to run

```
python3 -m scorep_trace <script.py>
```

The usual Score-P environment Variables will be respected. Please have a look at:

[www.vi-hps.org](http://www.vi-hps.org/projects/score-p/)

and

[Score-P Documentation](https://silc.zih.tu-dresden.de/scorep-current/pdf/scorep.pdf)

# Compatibility
The installation script works with python3. Python2 is not tested.

# Tracing
The tracing uses Score-P User instrumentation. The python trace module was reworked, to pass the region names to ```SCOREP_USER_REGION_BY_NAME_BEGIN(name,type)``` and ```SCOREP_USER_REGION_BY_NAME_END(name)``` instead of printing. All other features of the tracing module where striped.
