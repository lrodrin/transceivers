def my_callback(val):
    print("function my_callback was called with {0}".format(val))


def caller(val, func):
    func(val)


for i in range(5):
    caller(i, my_callback)
