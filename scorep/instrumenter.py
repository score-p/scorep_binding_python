import inspect
import os

global_instrumenter = None


def get_instrumenter(enable_instrumenter=False,
                     instrumenter_type="dummy"):
    """
    returns an instrumenter

    @param enable_instrumenter True if the Instrumenter should be enabled when run is called
    @param instrumenter_type which python tracing interface to use.
           Currently available: `profile` (default), `trace` and `dummy`
    """
    global global_instrumenter
    if global_instrumenter is None:
        if instrumenter_type == "profile":
            from scorep._instrumenters.scorep_profile import ScorepProfile
            global_instrumenter = ScorepProfile(enable_instrumenter)
        elif instrumenter_type == "trace":
            from scorep._instrumenters.scorep_trace import ScorepTrace
            global_instrumenter = ScorepTrace(enable_instrumenter)
        elif instrumenter_type == "dummy":
            from scorep._instrumenters.dummy import ScorepDummy
            global_instrumenter = ScorepDummy(enable_instrumenter)
        elif instrumenter_type == "cTrace":
            from scorep._instrumenters.scorep_cTrace import ScorepCTrace
            global_instrumenter = ScorepCTrace(enable_instrumenter)
        elif instrumenter_type == "cProfile":
            from scorep._instrumenters.scorep_cProfile import ScorepCProfile
            global_instrumenter = ScorepCProfile(enable_instrumenter)
        else:
            raise RuntimeError('instrumenter_type "{}" unkown'.format(instrumenter_type))

    return global_instrumenter


def register():
    """
    Reenables the python-tracing.
    """
    get_instrumenter().register()


def unregister():
    """
    Disables the python-tracing.
    Disabling the python-tracing is more efficient than disable_recording,
    as python does no longer call the tracing module.
    However, all the other things that are traced by Score-P will still be recorded.
    Please call register() to enable tracing again.
    """
    get_instrumenter().unregister()


class enable():
    """
    Context manager to enable tracing in a certain region:
    ```
    with enable(region_name=None):
        do stuff
    ```
    This overides --noinstrumenter (--nopython legacy)
    If a region name is given, the region the contextmanager is active will be marked in the trace or profile
    """

    def __init__(self, region_name=None):
        self.region_name = region_name

    def __enter__(self):
        self.tracer_registered = get_instrumenter().get_registered()
        if not self.tracer_registered:
            if self.region_name:
                self.module_name = "user_instrumenter"
                frame = inspect.currentframe().f_back
                file_name = frame.f_globals.get('__file__', None)
                line_number = frame.f_lineno
                if file_name is not None:
                    full_file_name = os.path.abspath(file_name)
                else:
                    full_file_name = "None"

                get_instrumenter().region_begin(
                    self.module_name, self.region_name, full_file_name,
                    line_number)

            get_instrumenter().register()

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.tracer_registered:
            get_instrumenter().unregister()

            if self.region_name is not None:
                get_instrumenter().region_end(
                    self.module_name, self.region_name)


class disable():
    """
    Context manager to disable tracing in a certain region:
    ```
    with disable():
        do stuff
    ```
    This overides --noinstrumenter (--nopython legacy)
    If a region name is given, the region the contextmanager is active will be marked in the trace or profile
    """

    def __init__(self, region_name=None):
        self.region_name = region_name

    def __enter__(self):
        self.tracer_registered = get_instrumenter().get_registered()
        if self.tracer_registered:
            get_instrumenter().unregister()

            if self.region_name is not None:
                self.module_name = "user_instrumenter"
                frame = inspect.currentframe().f_back
                file_name = frame.f_globals.get('__file__', None)
                line_number = frame.f_lineno
                if file_name is not None:
                    full_file_name = os.path.abspath(file_name)
                else:
                    full_file_name = "None"

                get_instrumenter().region_begin(
                    self.module_name, self.region_name, full_file_name,
                    line_number)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.tracer_registered:
            if self.region_name is not None:
                get_instrumenter().region_end(
                    self.module_name, self.region_name)

            get_instrumenter().register()
