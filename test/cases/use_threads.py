import random
import threading
import time
import instrumentation2


def worker(id, func):
    print("Thread %s started" % id)
    # Use a random delay to add non-determinism to the output
    time.sleep(random.uniform(0.01, 0.9))
    func()


def foo():
    print("hello world")
    t1 = threading.Thread(target=worker, args=(0, instrumentation2.bar))
    t2 = threading.Thread(target=worker, args=(1, instrumentation2.baz))
    t1.start()
    t2.start()


foo()
