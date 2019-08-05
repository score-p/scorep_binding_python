import inspect
import os.path
import scorep.trace


def register():
    """
    Reenables the python-tracing.
    """
    scorep.trace.get_tracer().register()


def unregister():
    """
    Disables the python-tracing.
    Disabling the python-tracing is more efficient than disable_recording, as python does not longer call the tracing module.
    However, all the other things that are traced by Score-P will still be recorded.
    Please call register() to enable tracing again.
    """
    scorep.trace.get_tracer().unregister()


class enable():
    """
    Context manager to enable tracing in a certain region:
    ```
    with enable():
        do stuff
    ```
    This overides --no-instrumenter (--nopython leagacy)
    """

    def __init__(self):
        pass

    def __enter__(self):
        self.tracer_registered = scorep.trace.get_tracer().register()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracer_registered = scorep.trace.get_tracer().unregister()


class disable():
    """
    Context manager to disable tracing in a certain region:
    ```
    with disable():
        do stuff
    ```
    This overides --no-instrumenter (--nopython leagacy)
    """

    def __init__(self):
        pass

    def __enter__(self):
        self.tracer_registered = scorep.trace.get_tracer().unregister()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracer_registered = scorep.trace.get_tracer().register()
