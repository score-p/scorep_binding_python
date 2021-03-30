import random
import threading
import time
import instrumentation2


lock = threading.Lock()


def worker(id, func):
    with lock:
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
    t1.join()
    t2.join()


foo()
