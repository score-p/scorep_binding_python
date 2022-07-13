import sys
import subprocess
import re


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


def call_otf2_print(trace_path):
    trace, std_err = call(["otf2-print", str(trace_path)])
    return trace, std_err


class OTF2_Region:
    def __init__(self, region):
        self.region = region

    def __str__(self):
        return self.region


class OTF2_Parameter:
    def __init__(self, parameter, value):
        self.parameter = parameter
        self.value = value

    def __str__(self):
        return "{}:{}".format(self.parameter, self.value)


class OTF2_Trace:
    def __init__(self, trace_path):
        self.path = trace_path
        self.trace, self.std_err = call_otf2_print(self.path)
        assert self.std_err == ""

    def __contains__(self, otf2_element):
        result = []
        if isinstance(otf2_element, OTF2_Region):
            for event in ("ENTER", "LEAVE"):
                search_str = "{event}[ ]*[0-9 ]*[0-9 ]*Region: \"{region}\"".format(
                    event=event, region=otf2_element.region)
                search_res = re.search(search_str, self.trace)
                result.append(search_res is not None)
        elif isinstance(otf2_element, OTF2_Parameter):
            search_str = "PARAMETER_STRING[ ]*[0-9 ]*[0-9 ]*Parameter: \"{parameter}\" <[0-9]*>, Value: \"{value}\""
            search_str = search_str.format(parameter=otf2_element.parameter, value=otf2_element.value)
            search_res = re.search(search_str, self.trace)
            result.append(search_res is not None)
        else:
            raise NotImplementedError
        return all(result)

    def findall(self, otf2_element):
        result = []
        if isinstance(otf2_element, OTF2_Region):
            for event in ("ENTER", "LEAVE"):
                search_str = "{event}[ ]*[0-9 ]*[0-9 ]*Region: \"{region}\"".format(
                    event=event, region=otf2_element.region)
                search_res = re.findall(search_str, self.trace)
                result.extend(search_res)
        else:
            raise NotImplementedError
        return result

    def __str__(self):
        return self.trace
