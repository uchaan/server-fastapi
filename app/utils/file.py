"""
로컬에 저장된 파일들을 관리하는 모듈
"""

import os

from loguru import logger


class FileManager:
    @staticmethod
    def remove_files_in_dir(dir_path) -> bool:
        success = True
        for filename in os.listdir(dir_path):
            try:
                os.remove(dir_path + filename)
            except Exception as e:
                logger.info(f"{e} raised while remove files in {dir_path}")
                success = False

        return success
