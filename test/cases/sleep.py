import time


def pointless_sleep():
    time.sleep(5)


def baz():
    print("Nice you are here.")


def foo():
    print("Hello world.")
    if True:
        pointless_sleep()
    baz()
    print("Good by.")


foo()
