import dis


def bar(a, b=None):
    pass


def foo():
    bar(1, {'ak': 'av'})


print(dis.dis(foo))
