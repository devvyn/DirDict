"""
File operation function wrappers, suitable for dictionary-like behaviour in an OS file system
"""

import os
from datetime import timedelta, datetime
from shutil import rmtree
from typing import List, Union, Set

from storage.file_system.types import T, BufferedIO


def init_directory(path: T, mode: int = 0o750, exist_ok: bool = True) -> None:
    """
    Create a storage directory, if one does not exist

    :param path: Path to create as storage directory
    :param mode: Directory permissions, passed to OS
    :param exist_ok: Suppress directory exists error
    """
    os.makedirs(path, mode=mode, exist_ok=exist_ok)


def remove_directory(path: T) -> None:
    """
    Explicitly delete the files on disk, thus clearing the cache instance in the specified directory
    """
    rmtree(path=path)


def values(path: T) -> List[T]:
    """
    Wrapper for os.listdir(directory)

    :return: Names of all keys in directory, or an empty list
    """
    return os.listdir(path)


def get(path: T) -> BufferedIO:
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


def get_key_path(key: T, path: T) -> T:
    """
    Get the absolute path to the file that corresponds to the key

    """
    filename = mask_invalid_filename_characters(key)
    key_path = path.join(path, filename)
    return key_path


def mask_invalid_filename_character(x: T, excluded_characters: Set = {*'\/:*?"<>|'}) -> T:
    return x if x not in excluded_characters else '_'


def mask_invalid_filename_characters(text: T) -> str:
    """
    Mask invalid characters in the text

    :param text: Any arbitrary string of characters that can be interpreted as text
    :return: Filename composed of safe characters for all platforms
    """
    # @todo review unicode basics and ensure this function works internationally
    return str(mask_invalid_filename_character(x) for x in str(text))


def set_(path: T, value: T = None) -> Union[T, None]:
    """
    Create file at path specified in `path` argument, if it doesn't already exist,
    then write or overwrite file with `value`
    """
    with os.open(path, os.O_WRONLY) as file:
        file.write(value)
    return value


def del_(path: T) -> None:
    """
    Delete corresponding file from disk

    :param path: Key name
    :raises: KeyError
    """
    try:
        os.remove(path)
    except os.error:
        raise KeyError(path)


def get_file_age(path: T, datetime_=datetime.now()) -> timedelta:
    """
    Get file's age based on last modified time, relative to `datetime_`

    :param path: Path of file
    :param datetime_: datetime for which to calculate age
    :return:
    """
    return get_file_modified_time(path) - datetime_


def get_file_modified_time(path: T) -> datetime:
    """
    `datetime` wrapper for `os.path.getmtime(path)`

    :param path: Path of file
    :return: File modification time, as reported by OS
    """
    return datetime.fromtimestamp(os.path.getmtime(path))
