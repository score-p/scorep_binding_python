import scorep.user


@scorep.user.region()
def foo():
    print("hello world")


foo()
with scorep.instrumenter.disable():
    foo()
    with scorep.instrumenter.enable():
        foo()
