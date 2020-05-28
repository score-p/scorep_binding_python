import time


def pointless_sleep():
    time.sleep(5)


def baz():
    print("Nice you are here.")


def foo(sleep=False):
    print("Hello world.")
    if sleep:
        pointless_sleep()
    baz()
    print("Good by.")


foo()
