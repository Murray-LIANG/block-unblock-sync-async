import multiprocessing
import multiprocessing.dummy as multithread
import socket
import timeit


def blocking_way():
    s = socket.socket()
    s.connect(('example.com', 80))  # BLOCK
    request = 'GET / HTTP/1.0\r\nHost: google.com\r\n\r\n'
    s.send(request.encode('ascii'))
    response = b''
    while True:
        chunk = s.recv(4096)  # BLOCK
        if chunk:
            response += chunk
        else:
            break
    return response


def in_sync():
    return [blocking_way() for _ in range(10)]


def in_multiprocess():
    for _ in range(10):
        proc = multiprocessing.Process(target=blocking_way)
        proc.start()


def in_multithread():
    for _ in range(10):
        thread = multithread.DummyProcess(target=blocking_way)
        thread.start()


if __name__ == '__main__':
    print(timeit.repeat('in_sync()',
                        setup="from __main__ import in_sync",
                        number=3))
    print(timeit.repeat('in_multiprocess()',
                        setup="from __main__ import in_multiprocess",
                        number=3))
    print(timeit.repeat('in_multithread()',
                        setup="from __main__ import in_multithread",
                        number=3))
