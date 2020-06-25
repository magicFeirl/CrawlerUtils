# 简介

> 闲的无聊又写了个爬虫轮子，和上一个相比差别不大，不过这次加了些代码注释。

`crawler.py`内含一个多生产者消费者模型的基类，需要复写`onconnect`和`ondownload`方法。

`config.py`包含一些客户端设置（比如请求头、最大并发连接数），将该模块内的`Config`类实例化并传入`Crawler`的子类进行爬虫参数设置。

## 示例

一个无意义的脚本，使用 10 条协程并发请求百度 10 次。

```python
import asyncio

from config import Config
from crawler import Crawler


class BDCrawler(Crawler):
    def __init__(self, urls, config=None):
        super(BDCrawler, self).__init__(base_urls=urls, config=config)

    async def onconnect(self, resp, arg1):
        print(await resp.text())
        print(arg1)

    async def ondownload(self, resp):
        pass


async def main():
    config = Config(connect_num=10)

    BDC = BDCrawler(['https://www.baidu.com'], config=config)
    await BDC.run(('Hehe', )) # 给连接回调传参


if __name__ == '__main__':
    asyncio.run(main())

```

