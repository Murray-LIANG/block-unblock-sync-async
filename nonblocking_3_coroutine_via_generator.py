import selectors
import socket
import time

selector = selectors.DefaultSelector()
urls = {'/{}'.format(i if i else '') for i in range(10)}
urls_todo = set()
stopped = False


class Future(object):
    def __init__(self):
        self.result = None
        self._callbacks = []

    def add_done_callback(self, func):
        self._callbacks.append(func)

    def set_result(self, result):
        self.result = result
        for func in self._callbacks:
            func(self)


class Crawler(object):
    def __init__(self, url):
        self.url = url
        self.response = b''

    def get(self):
        s = socket.socket()
        s.setblocking(False)
        try:
            s.connect(('example.com', 80))
        except BlockingIOError:
            pass
        future = Future()

        def on_connected():
            future.set_result(None)

        selector.register(s.fileno(), selectors.EVENT_WRITE, on_connected)
        yield future

        selector.unregister(s.fileno())
        request = 'GET {} HTTP/1.0\r\nHost: example.com\r\n\r\n'.format(
            self.url)
        s.send(request.encode('ascii'))

        global stopped
        global urls_todo
        while True:
            future = Future()

            def on_readable():
                future.set_result(s.recv(4096))

            selector.register(s.fileno(), selectors.EVENT_READ, on_readable)
            chunk = yield future
            selector.unregister(s.fileno())
            if chunk:
                self.response += chunk
            else:
                urls_todo.remove(self.url)
                if not urls_todo:
                    stopped = True
                break


class Task(object):
    def __init__(self, coroutine):
        self.coroutine = coroutine
        future = Future()
        future.set_result(None)
        self.step(future)

    def step(self, future):
        try:
            next_future = self.coroutine.send(future.result)
        except StopIteration:
            return
        next_future.add_done_callback(self.step)


def event_loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()


def main():
    global urls_todo
    urls_todo = urls.copy()
    start = time.time()
    for url in urls_todo:
        crawler = Crawler(url)
        Task(crawler.get())
    event_loop()
    print(time.time() - start)


if __name__ == '__main__':
    # print(timeit.repeat('main()',
    #                     setup="from __main__ import main",
    #                     number=3))
    for _ in range(10):
        main()
