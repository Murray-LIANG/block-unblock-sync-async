import asyncio
import os

import aiohttp
import async_timeout


async def download_coroutine(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            filename = os.path.basename(url)
            with open(filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)

            return await response.release()


async def main(loop):
    urls = (
        "http://www.irs.gov/pub/irs-pdf/f1040.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040a.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040ez.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040es.pdf",
        "http://www.irs.gov/pub/irs-pdf/f1040sb.pdf"
    )
    async with aiohttp.ClientSession(loop=loop) as session:
        for url in urls:
            await download_coroutine(session, url)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))