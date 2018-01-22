import scorep

def foo():
    scorep.user_region_begin("test_region")
    print("hello world")
    scorep.user_region_end("test_region")

foo()
