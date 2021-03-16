import os

with open("test.txt", "w") as f:
    f.write("test")

with open("test.txt", "r") as f:
    data = f.read()
    print(data)

os.remove("test.txt")
