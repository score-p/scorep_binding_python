import time

def pointless_sleep():
    time.sleep(120)
    
def foo():
    print("hello world")
    if True:
        pointless_sleep()
    print("Good By.")

foo()
