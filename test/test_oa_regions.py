import scorep.user


def foo():
    scorep.user.oa_region_begin("test_region")
    print("hello world")
    scorep.user.oa_region_end("test_region")


foo()
