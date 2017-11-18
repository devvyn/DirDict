"""
File operation function wrappers, suitable for dictionary-like behaviour in an OS file system
"""

import os
from datetime import timedelta, datetime
from shutil import rmtree
from typing import List, Union

from storage.file_system import Text, BufferedIO


def init_directory(path: Text, mode=0o750, exist_ok: bool = True) -> None:
    """
    Create a storage directory, if one does not exist

    :param path: Path to create as storage directory
    :param mode: Directory permissions, passed to OS
    :param exist_ok: Suppress directory exists error
    """
    os.makedirs(path, mode=mode, exist_ok=exist_ok)


def remove_directory(path: Text) -> None:
    """
    Explicitly delete the files on disk, thus clearing the cache instance in the specified directory
    """
    rmtree(path=path)


def get_keys(path: Text) -> List[Text]:
    """
    Wrapper for os.listdir(directory)

    :return: Names of all keys in directory, or an empty list
    """
    return os.listdir(path)


def get_file(path: Text) -> BufferedIO:
    """
    Get the file contents from disk, if the key exists in the storage directory

    :return: File contents
    :raises: KeyError
    """
    try:
        with os.open(path, os.O_RDONLY) as file:
            file_read = file.read()
    except os.error:
        raise KeyError(path)
    return file_read


def get_key_path(key, path):
    key_path = path.join(path, key)
    return key_path


def set_file(path: Text, value: Union[Text, None]) -> None:
    """
    Create file named "key", if it doesn't already exist, then write or overwrite contexts with text
    """
    with os.open(path, os.O_WRONLY) as file:
        file.write(value)


def delete_file(path):
    """
    Delete corresponding file from disk

    :param path: Key name
    :raises: KeyError
    """
    try:
        os.remove(path)
    except os.error:
        raise KeyError(path)


def get_file_age(path: Text) -> timedelta:
    """
    Files age based on last modified time

    :param path:
    :return:
    """
    return get_file_modified_time(path) - datetime.now()


def get_file_modified_time(path: Text) -> datetime:
    return datetime.fromtimestamp(os.path.getmtime(path))
