import scorep.user


def foo():
    print("foo")


def bar():
    print("bar")


foo()
scorep.user.force_finalize()
bar()
