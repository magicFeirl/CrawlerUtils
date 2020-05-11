import os

import aiofiles

async def save_one(path, file_name, response):
    full_path = os.path.join(path, file_name)

    if not os.path.exists(full_path):
        async with aiofiles.open(full_path, 'wb') as f:
            while True:
                chunk = await response.content.read(64 * 1024)
                if not chunk:
                    break
                await f.write(chunk)
    else:
        print(full_path, '下已存在同名文件')

