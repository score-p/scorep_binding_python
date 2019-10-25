import scorep.instrumenters.dummy
import scorep.instrumenters.scorep_profile
import scorep.instrumenters.scorep_trace

global_instrumenter = None


def get_instrumenter(
        bindings=None,
        enable_instrumenter=False,
        instrumenter_type="dummy"):
    """
    returns an instrumenter

    @param bindings the c/c++ scorep bindings
    @param enable_instrumenter True if the Instrumenter should be enabled when run is called
    @param instrumenter_type which python tracing interface to use. Currently available: `profile` (default), `trace` and `dummy`
    """
    global global_instrumenter
    if global_instrumenter is None:
        if instrumenter_type == "profile":
            global_instrumenter = scorep.instrumenters.scorep_profile.ScorepProfile(
                bindings, enable_instrumenter)
        elif instrumenter_type == "trace":
            global_instrumenter = scorep.instrumenters.scorep_trace.ScorepTrace(
                bindings, enable_instrumenter)
        elif instrumenter_type == "dummy":
            global_instrumenter = scorep.instrumenters.dummy.ScorepDummy(
                enable_instrumenter)
        else:
            raise RuntimeError(
                "instrumenter_type \"{}\" unkown".format(instrumenter_type))

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
        self.tracer_registered = scorep.instrumenter.get_instrumenter().get_registered()
        if not self.tracer_registered:
            scorep.instrumenter.get_instrumenter().register()

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.tracer_registered:
            scorep.instrumenter.get_instrumenter().unregister()


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
        self.tracer_registered = scorep.instrumenter.get_instrumenter().get_registered()
        if self.tracer_registered:
            scorep.instrumenter.get_instrumenter().unregister()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.tracer_registered:
            scorep.instrumenter.get_instrumenter().register()
