import scorep
import test_instrumentation2


def foo():
    print("hello world")
    test_instrumentation2.baz()
    test_instrumentation2.bar()


with scorep.instrumenter.enable():
    foo()
