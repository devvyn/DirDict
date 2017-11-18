"""
The functions here are primarily concerned with mapping Python dict methods to
the built in file access functions.

I've chosen to express this API mapping layer in static functions
because this makes for good readability and easier automated testing.

For OOP, compose your class to call these functions from within the class or object scope.

For procedural programming, assign your local variables and have at it, you weirdo! ;-)

Warning: these functions are naive, and the underlying Python functions will raise OSError if you make
a mistake with a path. Use the normalize_file_name` function if you want to filter path segments individually,
though that won't protect you from using non-existent paths or permission-restricted paths.

    --Devvyn
"""

import os
from datetime import timedelta, datetime
from functools import partial
from shutil import rmtree
from typing import List, Union, Set

from storage.file_system.types import BytesOrText, BufferedIO


def initialize_base_path(path: BytesOrText, mode: int = 0o750, exist_ok: bool = True) -> None:
    """
    Create a storage directory, if one does not exist

    :param path: Path to create as storage directory
    :param mode: Directory permissions, passed to OS
    :param exist_ok: Suppress directory exists error
    """
    os.makedirs(path, mode=mode, exist_ok=exist_ok)


def remove_base_path(path: BytesOrText) -> None:
    """
    Explicitly delete the path from the file system, thus deleting all contained files

    :raises: OSError
    """
    rmtree(path=path)


def keys(path: BytesOrText) -> List[BytesOrText]:
    """
    Wrapper for os.listdir(directory)

    :return: Names of all files in directory, or an empty list
    :raises: OSError
    """
    return os.listdir(path)


def get(path: BytesOrText) -> BufferedIO:
    """
    Get the file contents from disk, if the file exists in the storage directory

    :return: File contents
    :raises: OSError
    """
    with os.open(path, os.O_RDONLY) as file:
        file_read = file.read()
    return file_read


def get_key_path(base_path: BytesOrText, key: BytesOrText) -> BytesOrText:
    """
    Get the absolute path to the file that corresponds to the key

    The path will be the base path joined to a mangled version of the key. This is done to crudely ensure
    cross-platform compatibility.

    """
    filename = normalize_file_name(key)
    # noinspection PyTypeChecker
    return os.path.join(base_path, filename)


def replace_character(character: BytesOrText, excluded_characters: Set = {*'\/:*?"<>|'},
                      mask='_') -> BytesOrText:
    return character if character not in excluded_characters else mask


def normalize_file_name(text: BytesOrText, mask='_') -> str:
    """
    Mask invalid characters in the text by substitution, and convert to lower case

    :param mask: String to substitute for invalid characters
    :param text: Any arbitrary string of characters that can be interpreted as text
    :return: Filename composed of safe characters for all platforms
    """
    mask_invalid_filename_character_underscore = partial(replace_character, mask=mask)
    # @todo review unicode basics and ensure this function works internationally, something doesn't feel right about arg and return type mismatch
    masked = str(mask_invalid_filename_character_underscore(character) for character in text)
    lowered = masked.lower()
    return lowered


def set_(path: BytesOrText, value: BytesOrText = None) -> Union[BytesOrText, None]:
    """
    Create file at path specified in `path` argument, if it doesn't already exist,
    then write or overwrite file contents with raw `value`
    """
    with os.open(path, os.O_WRONLY) as file:
        file.write(value)
    return value


def del_(path: BytesOrText) -> None:
    """
    Delete corresponding file from disk

    :param path: Key name
    :raises: OSError
    """
    os.remove(path)


def get_file_age(path: BytesOrText, later=datetime.now()) -> timedelta:
    """
    Get file's age based on last modified time, relative to `later`

    :param path: Path of file
    :param later: datetime for which to calculate age
    :return:
    """
    return get_file_modified_time(path) - later


def get_file_modified_time(path: BytesOrText) -> datetime:
    """
    `datetime` wrapper for `os.path.getmtime(path)`

    :param path: Path of file
    :return: File modification time, as reported by OS
    """
    return datetime.fromtimestamp(os.path.getmtime(path))


def dir_len(path):
    return len(keys(path))
