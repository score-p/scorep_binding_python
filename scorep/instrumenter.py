import scorep.instrumenters.dummy
import scorep.instrumenters.scorep_profile


global_instrumenter = None


def get_instrumenter(bindings=None, enable_instrumenter=False):
    global global_instrumenter
    if global_instrumenter is None:
        if bindings is None:
            global_instrumenter = scorep.instrumenters.dummy.DummyTrace(enable_instrumenter)
        else:
            global_instrumenter = scorep.instrumenters.scorep_profile.ScorepTrace(
                bindings, enable_instrumenter)
    return global_instrumenter


def register():
    """
    Reenables the python-tracing.
    """
    get_instrumenter().register()


def unregister():
    """
    Disables the python-tracing.
    Disabling the python-tracing is more efficient than disable_recording, as python does not longer call the tracing module.
    However, all the other things that are traced by Score-P will still be recorded.
    Please call register() to enable tracing again.
    """
    get_instrumenter().unregister()


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
        self.tracer_registered = get_instrumenter().register()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracer_registered = get_instrumenter().unregister()


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
        self.tracer_registered = get_instrumenter().unregister()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tracer_registered = get_instrumenter().register()
