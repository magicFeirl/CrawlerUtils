'''下载器类
提供了异步保存文件和一些操作文件方法

TODO: 设置请求信息 2020年7月22日14:21:14'''
import os

import asyncio
import aiohttp
import aiofiles

class Downloader(object):

    @classmethod
    def is_file_exists(cls, filename, dest='.'):
        '''判断文件是否存在
        filename: 文件名
        dest:     目标路径'''

        fullpath = os.path.join(dest, filename)
        return os.path.isfile(fullpath) and os.path.exists(fullpath)

    @classmethod
    def mkdir(cls, dest):
        '''如果文件夹不存在则创建文件夹 返回传入的文件夹路径'''
        if not os.path.isdir(dest) and not os.path.exists(dest):
            os.makedirs(dest)

        return dest

    @classmethod
    def get_basename(cls, url):
        return os.path.basename(url)

    @classmethod
    async def async_download(cls, resp, filename=None, dest='.',
    cover=False, mkdirs=True, timeout=60*3, chunk_size=1024*1024*3):
        '''
        下载单个文件
        resp: 一个 aiohttp.ClientResponse 对象，用来请求并下载文件
        filename: 保存的文件名，如果为 None 则是否请求网址的文件名
        dest:     保存的目标路径，默认为当前文件夹
        cover:    如果目标路径下已经有同名文件存在，是否覆盖，默认为否
        mkdir:    目标路径文件夹不存在的话是否创建文件夹，默认为是（貌似也只能为是~）
        timeout:  请求超时，默认 3 分钟
        chunk_size: 读文件的块大小，默认为最大 3 MB
        '''
        uri = str(resp.url) # 提取url

        if mkdirs:
            cls.mkdir(dest)

        filename = filename if filename else cls.get_basename(uri) # 获取文件名
        # filename = filename.replace('?', '_')
        fullpath = os.path.join(dest, filename) # 获取文件全路径

        if os.path.exists(fullpath) and not cover:
            print(f'{fullpath} is already existed.')
        else:
            print(f'Start downloading {filename}')
            try:
                async with aiofiles.open(fullpath, 'wb') as file:
                    while True: # 分块大法
                        content = await resp.content.read(chunk_size)
                        if not content:
                            break
                        await file.write(content)
            except asyncio.CancelledError:
                raise
            except IOError as ie:
                print(f'IOError: {str(ie)} type: {type(ie)}')
            except TimeoutError:
                print(f'请求-下载 {filename} 超时')
            except Exception as e:
                print(f'下载文件发生异常: {str(e)} type: {type(e)}')

    @classmethod
    async def async_download_many(cls, pair, limit=0, dest='.',
    cover=False, timeout=60*3, chunk_size=1024*1024*10):
        '''下载多个文件，和下载单个文件不同的是这里传入的是 pair 列表，内含 URL 和文件名
        pair: url & 文件名列表 [('http://...', '123.jpg'), ...]，文件名可传入 None
        limit: 最大并发下载数，默认为 20 条，传入 0 表示无限制
        其余参数同 async_download
        '''
        limit = limit if limit > 0 else len(pair)
        conn = aiohttp.TCPConnector(limit=limit) # 连接请求池大小
        begin = 0 # 分块的起始下标

        # 在外层创建文件夹
        cls.mkdir(dest)

        async def inner(item, client):
            '''下载回调'''
            if not Downloader.is_file_exists(item[1], dest) \
            and not Downloader.is_file_exists(Downloader.get_basename(item[1])):
                async with client.get(item[0]) as resp:
                    # 实际调用的还是单个下载方法
                    # 由于外部已经创建文件夹，所以这里 mkdirs 传 False
                    await cls.async_download(resp, item[1], dest, cover,
                    False, timeout, chunk_size)

        async with aiohttp.ClientSession(connector=conn) as client:
            await asyncio.gather(*[inner(item, client)
            for item in pair], return_exceptions=False)


async def main():
    urls = [
    ('https://img2.gelbooru.com/samples/45/e2/sample_45e2adc9bfd738f5823818be74c283ca.jpg', None),
('https://img2.gelbooru.com/samples/86/b7/sample_86b7e29387ee345f3f89e85308acd62f.jpg', None),
('https://img2.gelbooru.com/samples/7f/26/sample_7f267e0ad1761827ddd0943108cdbff1.jpg', None),]

    '''
    async with aiohttp.ClientSession() as client:
        async with client.get(url) as resp:
            await Downloader.async_download(resp)
    '''
    await Downloader.async_download_many(urls, dest='feelot')


if __name__ == '__main__':

    asyncio.run(main())
