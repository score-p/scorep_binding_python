

class TestClass:
    def foo(self):
        print("foo")
    def doo(arg):
        print("doo")
        arg.foo()


def foo():
    print("bar")
    
    def doo(arg):
        print("asdgh")
    doo("test")
    
if __name__ == "__main__":
    t = TestClass()
    
    
    t.doo()
    foo()