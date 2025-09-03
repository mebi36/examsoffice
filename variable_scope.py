# a global variable
a = 50

def function():
    global a
    a += 1
    print(a)

function()
print(a)