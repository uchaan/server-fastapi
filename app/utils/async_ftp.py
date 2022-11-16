"""
aioftp 를 사용하여 asynchronous 하게 FTP 업로드를 관리해주는 모듈
"""

import os

from loguru import logger
import aioftp


class AsyncFtpManager:
    def __init__(self):
        self.client = aioftp.Client()

    async def connect(self, host, port, username, password):
        await self.client.connect(host, port)
        await self.client.login(user=username, password=password)

    async def upload(self, path: str, file_path: str, file_name: str) -> bool:
        await self.client.change_directory(path=path)
        try:
            await self.client.upload(file_path, file_name, write_into=True)

        except Exception as e:
            logger.info(f"{e} raised while ftp file uploading...")
            return False

        else:
            return True

    async def upload_dir(self, path: str, dir_path, mkdir=False):
        """
        로컬 dir_path 에 있는 모든 파일들을 호스트의 path 디렉토리에 FTP 로 모두 업로드함.
        """
        success = True

        if mkdir:
            await self.client.make_directory(path=path)

        await self.client.change_directory(path=path)

        for filename in os.listdir(dir_path):
            try:
                await self.client.upload(dir_path + filename, filename, write_into=True)
                # await self.client.upload(dir_path + filename)
            except Exception as e:
                logger.info(f"{e} raised while ftp file uploading...")
                success = False

        return success

    async def close(self):
        await self.client.quit()
