import scorep.user
import scorep.instrumenter


def foo():
    with scorep.user.region("test_region"):
        print("hello world")


def bar():
    with scorep.instrumenter.enable():
        foo()
        with scorep.instrumenter.disable():
            foo()


foo()
bar()
