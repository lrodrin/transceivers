def my_callback(val):
    print("CURRENT RUNNING CONFIG {0}".format(val))
    return val

def caller(val, func):
    return func(val)


# for i in range(5):
    # caller(i, my_callback)
