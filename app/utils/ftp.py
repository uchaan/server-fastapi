"""
FTP 파일 업로드, 디렉토리 생성, 파일리스트 가져오기, 등을 관리해주는 모듈
"""

import os
import ftplib
from datetime import datetime

from loguru import logger


class FtpManager:
    def __init__(self, host, port, username, password, path):
        self.path = path
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port)
        self.ftp.login(user=username, passwd=password)
        self.ftp.encoding = "euc-kr"

    def upload(self, file_path: str, file_name: str):
        self.ftp.cwd(self.path)
        try:
            with open(file_path, "rb") as f:
                response = self.ftp.storbinary("STOR " + file_name, f)
                logger.info(response)

                if response[0] == "5":
                    return False

        except:
            logger.info("something wrong with ftp upload")
            return False

        return True

    def make_dir(self, dir_name: str):
        self.ftp.mkd(self.path + "/" + dir_name)

    def file_list(self, dir_name: str):
        self.ftp.encoding = "utf-8"
        self.ftp.cwd(f"{self.path}/{dir_name}")
        res = self.ftp.nlst()
        self.ftp.encoding = "euc-kr"
        return res

    def upload_dir(self, dir_path: str, mkdir=False):
        """
        로컬의 {dir_path} 에 있는 파일들을 모두 호스트의 {path} 로 업로드해줌
        """

        success = True
        self.ftp.cwd(self.path)

        if mkdir:
            date = f"{datetime.now().strftime('%Y-%m-%d')}"
            try:
                self.ftp.mkd(date)
            except:
                pass
            self.ftp.cwd(self.path + "/" + date)

        for filename in os.listdir(dir_path):
            try:
                with open(dir_path + filename, "rb") as f:
                    response = self.ftp.storbinary("STOR " + filename, f)
                    logger.info(response)

                    if response[0] == "5":
                        success = False

            except Exception as e:
                logger.info(f"{e} raised while ftp file uploading...")
                success = False

        return success

    def close(self):
        self.ftp.quit()
