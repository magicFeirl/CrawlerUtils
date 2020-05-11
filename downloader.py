import asyncio

from aiohttp import ClientSession
from client_config import ClientConfig


class Downloader():
    def __init__(self, ccf=None):
        self.ccf = ccf if ccf else ClientConfig()

        self.connect_queue = asyncio.Queue()
        self.download_queue = asyncio.Queue()

    def init_connect_queue(self, urls):
        for url in list(urls):
            self.connect_queue.put_nowait(url)

    async def connect(self):
        while True:
            url = await self.connect_queue.get()

            async with self.session.get(url, headers=self.ccf.headers,
            proxy=self.ccf.proxy) as resp:
                await self.connect_callback(resp)

            self.connect_queue.task_done()

    async def download(self):
        while True:
            url = await self.download_queue.get()

            async with self.session.get(url, headers=self.ccf.headers,
            proxy=self.ccf.proxy) as resp:
                await self.download_callback(resp)

            self.download_queue.task_done()

    async def connect_callback(self, response):
        print('ConnectCallback:')
        print(response.status)

    async def download_callback(self, response):
        print('DownloadCallaback:')
        print(response.status)

    async def clear_connect_queue(self):
        while not self.connect_queue.empty():
            await self.connect_queue.get()
            self.connect_queue.task_done()

    async def create_tasks(self):
        tasks = []
        for i in range(self.ccf.max_connect_num):
            tasks.append(asyncio.create_task(self.connect()))
            await asyncio.sleep(0)

        for i in range(self.ccf.max_download_num):
            tasks.append(asyncio.create_task(self.download()))
            await asyncio.sleep(0)

        await self.connect_queue.join()
        await self.download_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def start(self):
        async with ClientSession(timeout=self.ccf.timeout) as session:
            self.session = session

            await self.create_tasks()
