import utils


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, utils.OTF2_Region) and isinstance(right, utils.OTF2_Trace):
        if op == "in":
            output = ["Region \"{}\" ENTER or LEAVE not found in trace:".format(left)]
            for line in str(right).split("\n"):
                output.append("\t" + line)
            return output
        elif op == "not in":
            output = ["Unexpected region \"{}\" ENTER or LEAVE found in trace:".format(left)]
            for line in str(right).split("\n"):
                output.append("\t" + line)
            return output
    elif isinstance(left, utils.OTF2_Parameter) and isinstance(right, utils.OTF2_Trace) and op == "in":
        output = ["Parameter \"{parameter}\" with Value \"{value}\" not found in trace:".format(
            parameter=left.parameter,
            value=left.value)]
        for line in str(right).split("\n"):
            output.append("\t" + line)
        return output
