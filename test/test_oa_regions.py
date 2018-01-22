import scorep

def foo():
    scorep.oa_region_begin("test_region")
    print("hello world")
    scorep.oa_region_end("test_region")

foo()
