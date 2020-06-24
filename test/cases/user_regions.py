import scorep.user
import scorep.instrumenter


def foo():
    scorep.user.region_begin("test_region")
    print("hello world")
    scorep.user.region_end("test_region")


def foo2():
    with scorep.user.region("test_region_2"):
        print("hello world")


@scorep.user.region()
def foo3():
    print("hello world3")


@scorep.user.region("test_region_4")
def foo4():
    print("hello world4")


foo()
foo2()
with scorep.instrumenter.enable():
    foo3()
with scorep.instrumenter.disable():
    foo3()
foo4()
