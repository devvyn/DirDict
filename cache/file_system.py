import os
from datetime import time
from genericpath import exists
from shutil import rmtree

import requests


class FileSystemCache:
    """Use the file system as a key-value store, with file modified date as expiration indicator"""
    mode = 0o640
    directory = '.web_rips'

    def __init__(self, directory=directory):
        self.init(directory=directory)

    @staticmethod
    def init(directory: (bytes or str) = directory) -> None:
        """
        Explicitly create a cache directory, if one does not exist

        :param directory:
        """
        os.makedirs(directory, mode=FileSystemCache.mode, exist_ok=True)

    @staticmethod
    def purge(directory: (bytes or str) = directory) -> None:
        """
        Explicitly delete the files on disk, thus clearing all cache instances in the specified directory

        :param directory:
        """
        rmtree(directory)

    @staticmethod
    def get(key):
        # read file if exist and not expired,

        if exists(key) and os.path.getmtime(key) - time():
            with os.open(key, os.O_RDONLY, mode=FileSystemCache.mode) as file:
                return file.read()
        # fetch from URL and write to file if not
        response = requests.get(key)
        response.raise_for_status()
        return response
        # always return non-null value or raise exception

    def delete(self, key):
        # delete file if exist,
        # raise exception if not
        ...

    def clean(self):
        for filename in (key for key in self.keys() if key.expired):
            self.delete(filename)

    def keys(self):
        # get filenames in cache directory
        return os.listdir()

    def items(self):
        # get filenames and file reader partials
        raise NotImplemented(f'{__name__} is not implemented')
