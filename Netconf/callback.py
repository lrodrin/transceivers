def my_callback(val):
    print("CURRENT RUNNING CONFIG {0}".format(val))

def caller(val, func):
    func(val)


# for i in range(5):
    # caller(i, my_callback)
