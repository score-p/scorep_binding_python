import importlib
import os

data1 = """
def foo():
    print("foo1")
"""

data2 = """
def foo(arg):
    print(arg)
def bar():
    print("bar")
"""


with open("reload_test.py","w") as f:
    f.write(data1)

import reload_test
reload_test.foo()

importlib.reload(reload_test)
reload_test.foo()


with open("reload_test.py","w") as f:
    f.write(data2)

importlib.reload(reload_test)
reload_test.foo("foo2")
reload_test.bar()

os.remove("reload_test.py")

