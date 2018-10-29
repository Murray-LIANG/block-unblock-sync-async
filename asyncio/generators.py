# Some notes of https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/

"""
The one doesn't use the generator. It populates the number in range in `seq`
(memory).
"""
def eager_range(end):
    seq = []
    index = 0
    while index < end:
        seq.append(index)
        index += 1
    return seq


"""
Uses the generator (`yield` keyword). 
"""
def lazy_range(end):
    index = 0
    while index < end:
        yield index
        index += 1


"""
Then need a way to send a value back to a generator. `send` function added.

Usage:
    g = jumping_range(5)
    print(next(g))  # 0
    print(g.send(2))  # 2
    print(next(g))  # 3
    print(g.send(-1))  # 2
    for i in g:
        print(i)  # 3, 4
"""
def jumping_range(end):
    index = 0
    while index < end:
        jump = yield index
        if jump is None:
            jump = 1
        index += jump


"""
Then `yield from` was added to: a) make yield from another generator more
easier (no need to write a while loop to iterate another generator, b) chain
the generators together.

Usage:
    g = top()
    value = next(g)
    print(value)  # 42
    value = g.send(value * 2)
    # Traceback (most recent call last):
    #     File "/home/liangr/git/asyncio/generators.py", line 65, in <module>
    #         value = g.send(value * 2)
    # StopIteration: 84
    
"""
def bottom():
    return (yield 42)

def middle():
    return (yield from bottom())

def top():
    return (yield from middle())


"""
How asynchronous programming in Python3.4
Python3.4 introduced `asyncio` with event loop and related module as the
framework. It decorates the functions as coroutines using `asyncio.coroutine`
to make them different from the general generators.
"""
import asyncio

@asyncio.coroutine
def countdown(number, n):
    while n >= 0:
        print('T-minus', n, '({})'.format(number))
        # 1. Return `asyncio.Future` then pause.
        # 2. The Future object will be passed to event loop.
        # 3. The event (1 sec later) happens, event loop knows the Future and
        #    coroutine of the event, then calls `send` to resume the coroutine
        yield from asyncio.sleep(1)
        n -= 1

def main():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(countdown('A', 2)),
        asyncio.ensure_future(countdown('B', 4))
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

if __name__ == '__main__':
    main()
