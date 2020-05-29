import instrumentation2


def foo():
    print("hello world")
    instrumentation2.baz()
    instrumentation2.bar()


foo()
