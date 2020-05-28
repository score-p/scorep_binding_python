import sys


def main(argv=None):
    print("successfully called main")


sys.modules['__main__'].main(sys.argv)
