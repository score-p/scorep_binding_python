import scorep.user


def bar():
    print("hello world")


def foo():
    bar()
    scorep.user.rewind_begin("test_region")
    bar()
    scorep.user.rewind_end("test_region", True)


foo()
