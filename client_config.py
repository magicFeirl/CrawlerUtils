from aiohttp import ClientTimeout

class ClientConfig():
    def __init__(self, timeout=60, headers=None, port=None,
    max_connect_num=1, max_download_num=1):
        self.proxy = None
        self.timeout = ClientTimeout(total=timeout)

        self.headers = headers

        if not self.headers:
            self.headers = {'User-Agent': 'wasp'}
        if port:
            self.proxy = f'http://127.0.0.1:{port}'

        self.max_connect_num = max_connect_num
        self.max_download_num = max_download_num
