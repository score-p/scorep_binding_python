import scorep.user
import scorep.instrumenter


class TestClass:
    def foo(self):
        print("foo")

    def doo(arg):
        print("doo")
        arg.foo()


class TestClass2:
    @scorep.user.region()
    def foo(self):
        print("foo-2")


def foo():
    print("bar")

    def doo(arg):
        print("asdgh")
    doo("test")


if __name__ == "__main__":
    t = TestClass()
    t2 = TestClass2()

    t2.foo()
    t.doo()
    foo()

    with scorep.instrumenter.disable():
        t2.foo()
