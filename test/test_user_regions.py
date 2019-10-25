import scorep.user


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


foo()
foo2()
foo3()
