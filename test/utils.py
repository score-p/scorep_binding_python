import sys
import subprocess
import otf2


def call(arguments, expected_returncode=0, env=None):
    """
    Calls the command specificied by arguments and checks the returncode via assert
    return (stdout, stderr) from the call to subprocess
    """
    if sys.version_info > (3, 5):
        out = subprocess.run(
            arguments, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            assert out.returncode == expected_returncode
        except AssertionError as e:
            e.args += ("stderr: {}".format(out.stderr.decode("utf-8")),)
            raise
        stdout, stderr = (out.stdout, out.stderr)
    else:
        p = subprocess.Popen(
            arguments, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate()
        try:
            assert p.returncode == expected_returncode
        except AssertionError as e:
            e.args += ("stderr: {}".format(stderr.decode("utf-8")),)
            raise
    return stdout.decode("utf-8"), stderr.decode("utf-8")


def call_with_scorep(file, scorep_arguments=None, expected_returncode=0, env=None):
    """
    Shortcut for running a python file with the scorep module

    @return (stdout, stderr) from the call to subprocess
    """
    arguments = [sys.executable, "-m", "scorep"]
    if scorep_arguments:
        arguments.extend(scorep_arguments)
    return call(arguments + [str(file)], expected_returncode=expected_returncode, env=env)


def get_region_names(trace_path):
    with otf2.reader.open(trace_path) as trace:
        return [region.name for region in trace.definitions.regions]


def findall_regions(trace_path, region_name):
    with otf2.reader.open(trace_path) as trace:
        return [
            (location, event)
            for location, event in trace.events
            if isinstance(event, (otf2.events.Enter, otf2.events.Leave))
            and event.region.name == region_name
        ]
