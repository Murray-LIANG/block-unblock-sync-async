import datetime
import heapq
import time
import types


class Task(object):
    """Represents how long a coroutine should wait before starting again."""

    def __init__(self, wait_until, coro):
        self.coro = coro
        self.wait_until = wait_until

    def __eq__(self, other):
        return self.wait_until == other.wait_until

    def __lt__(self, other):
        return self.wait_until < other.wait_until


class SleepingLoop(object):
    """An event loop focused on delaying execution of coroutines."""

    def __init__(self, *coros):
        self._new = coros
        self._waiting = []

    def run_until_complete(self):
        # Start all the coroutines
        for coro in self._new:
            wait_for = coro.send(None)
            heapq.heappush(self._waiting, Task(wait_for, coro))
        # Keep running until there is no more work to do.
        while self._waiting:
            now = datetime.datetime.now()
            task = heapq.heappop(self._waiting)
            if now < task.wait_until:
                delta = task.wait_until - now
                time.sleep(delta.total_seconds())
                now = datetime.datetime.now()

            try:
                wail_until = task.coro.send(now)
                heapq.heappush(self._waiting, Task(wail_until, task.coro))
            except StopIteration:
                # The coroutine is done.
                pass


@types.coroutine
def sleep(seconds):
    """Pauses a coroutine for the specified number of seconds."""
    now = datetime.datetime.now()
    wait_until = now + datetime.timedelta(seconds=seconds)

    actual = yield wait_until
    return actual - now


async def countdown(label, length, delay=0):
    """Countdowns a launch for `length` seconds, waiting `delay` seconds."""
    print(label, 'waiting', delay, 'seconds before starting countdown.')
    delta = await sleep(delay)
    print(label, 'starting after waiting', delta)
    while length:
        print(label, 'T-minus', length)
        waited = await sleep(1)
        length -= 1
    print(label, 'lift-off!')


def main():
    """Starts the event loop, counting down 3 separate launches."""
    loop = SleepingLoop(countdown('A', 5),
                        countdown('B', 3, delay=2),
                        countdown('C', 4, delay=1))
    start = datetime.datetime.now()
    loop.run_until_complete()
    print('total elapsed time is', datetime.datetime.now() - start)


if __name__ == '__main__':
    main()
