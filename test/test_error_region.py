import scorep.user


def foo():
    scorep.user.region_end("test_region")
    scorep.user.region_end("test_region_2")


foo()
