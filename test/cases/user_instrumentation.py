import scorep
import instrumentation2


def foo():
    print("hello world")
    instrumentation2.bar()


@scorep.instrumenter.enable()
def foo2():
    print("hello world2")
    instrumentation2.baz()


with scorep.instrumenter.enable():
    foo()

foo2()
