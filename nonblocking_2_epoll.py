import selectors
import socket
import time

selector = selectors.DefaultSelector()
urls = {'/{}'.format(i if i else '') for i in range(10)}
urls_todo = set()
stopped = False


class Crawler(object):
    def __init__(self, url):
        self.url = url
        self.socket = None
        self.response = b''

    def get(self):
        self.socket = socket.socket()
        self.socket.setblocking(False)
        try:
            self.socket.connect(('example.com', 80))
        except BlockingIOError:
            pass
        selector.register(self.socket.fileno(),
                          selectors.EVENT_WRITE,
                          self.send)

    def send(self, key, mask):
        selector.unregister(key.fd)
        request = 'GET {} HTTP/1.0\r\nHost: example.com\r\n\r\n'.format(
            self.url)
        self.socket.send(request.encode('ascii'))
        selector.register(key.fd, selectors.EVENT_READ, self.receive)

    def receive(self, key, mask):
        global stopped
        global urls_todo
        chunk = self.socket.recv(4096)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)
            urls_todo.remove(self.url)
            if not urls_todo:
                stopped = True


def event_loop():
    while not stopped:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback(event_key, event_mask)


def main():
    global urls_todo
    urls_todo = urls.copy()
    start = time.time()
    for url in urls_todo:
        crawler = Crawler(url)
        crawler.get()
    event_loop()
    print(time.time() - start)


if __name__ == '__main__':
    # print(timeit.repeat('main()',
    #                     setup="from __main__ import main",
    #                     number=3))
    for _ in range(10):
        main()
