import multiprocessing
import multiprocessing.dummy as multithread
import socket
import timeit


def nonblocking_way():
    s = socket.socket()
    s.setblocking(False)
    try:
        s.connect(('example.com', 80))  # BLOCK
    except BlockingIOError:
        pass
    request = 'GET / HTTP/1.0\r\nHost: example.com\r\n\r\n'
    data = request.encode('ascii')

    # Although not blocking, always trying to send data until succeed.
    while True:
        try:
            s.send(data)
            break  # try to send data until socket is ready.
        except OSError:
            pass

    response = b''
    while True:
        try:
            while True:
                chunk = s.recv(4096)  # not blocking any more.
                if not chunk:
                    break
                response += chunk
            break
        except OSError:
            pass
    return response


def in_sync():
    return [nonblocking_way() for _ in range(10)]


def in_multiprocess():
    for _ in range(10):
        proc = multiprocessing.Process(target=nonblocking_way)
        proc.start()


def in_multithread():
    for _ in range(10):
        thread = multithread.DummyProcess(target=nonblocking_way)
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
