import asyncio

urls = {'/{}'.format(i if i else '') for i in range(10)}
urls_todo = set()


@asyncio.coroutine
def get(url):
    print('get url: {}'.format(url))
    connect = asyncio.open_connection('example.com', 80)
    reader, writer = yield from connect
    request = 'GET {} HTTP/1.0\r\nHost: example.com\r\n\r\n'.format(url)
    writer.write(request.encode('ascii'))
    yield from writer.drain()
    while True:
        line = yield from reader.readline()
        if line == b'\r\n':
            break
        print('{} header: {}'.format(url, line.decode('ascii').rstrip()))

    writer.close()


loop = asyncio.get_event_loop()
tasks = [get(url) for url in urls]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
