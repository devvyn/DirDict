"""
The functions here are primarily concerned with mapping Python dict methods to
the built in file access functions, so "key" and "file" are interchangeable.

I've chosen to express core file system functions with this functional API
because this makes for good readability and easier automated testing.

Hierarchical structures are not supported, so no sub-directories.
This _could_ be supported in the future, however.

    --Devvyn
"""
from datetime import timedelta, datetime
from os import PathLike
from pathlib import Path, PurePath
from shutil import rmtree
from time import timezone
from typing import Union, Set

PathlibPath = Union[bytes, str, PathLike]


def initialize_base_path(path: PathlibPath, mode: int = 0o750, exist_ok: bool = True,
                         parents=True) -> None:
    """
    Create a storage directory, if one does not exist

    :param parents: Whether to create parent directories named by intermediate path segments or fail if they don't exist
    :param path: Path to create as storage directory
    :param mode: Directory permissions, passed to OS
    :param exist_ok: Suppress directory exists error
    """
    Path(path).mkdir(mode=mode, parents=parents, exist_ok=exist_ok)


def remove_base_path(path: PathlibPath) -> None:
    """
    Explicitly delete the path from the file system, thus deleting all contained files;
    makes no attempt to be smart about _not_ deleting things you _might_ have intended to keep!

    :param path: Path to destroy
    :raises: OSError
    """
    rmtree(path=path)


def keys(path: PathlibPath) -> Set[str]:  # @todo confirm whether bytes may be returned instead of str
    """
    Wrapper for os.listdir(directory)

    :return: Names of all files in directory, or an empty list
    :raises: OSError
    """
    return {*Path(path).iterdir()}


def get(path: PathlibPath) -> bytes:
    """
    Get the file contents from disk, if the file exists in the storage directory

    :return: File contents
    :raises: OSError
    """
    return Path(path).read_bytes()


def get_key_path(base_path: PathlibPath, key: str) -> PurePath:
    """
    Get the absolute path to the file that corresponds to the key

    The path will be the base path joined to a mangled version of the key. This is done to crudely ensure
    cross-platform compatibility.

    """
    return Path(base_path, key)


def set_(path: PathlibPath, data: bytes, mode=0o640) -> None:
    """
    Create file at path specified in `path` argument, if it doesn't already exist,
    then write or overwrite file contents with raw `value`

    :param path: Path to file to open for writing
    :param data: Bytes to write to file
    :param mode: Permissions mask to apply to file
    """
    p = Path(path)
    p.touch(mode=mode)
    p.write_bytes(data)


def del_(path: PathlibPath) -> None:
    """
    Delete file at `path`

    :param path: Path-like string pointing to file to delete
    :raises: OSError
    """
    Path(path).unlink()


def get_file_age(path: PathlibPath, relative_to: datetime = None, tz: timezone = None) -> timedelta:
    """
    Get file's age based on last modified time, relative to a given time.

    Timezone is gathered from `time` module at module load time.

    :param path: Path of file
    :param relative_to: datetime to which to compare; timezone should match that of file system records
    :param tz: Timezone; Default: local timezone
    :return:
    """
    if tz is None:
        tz = timezone
    if relative_to is None:
        relative_to = datetime.now(tz=tz)
    return get_file_modified_time(path, tz=tz) - relative_to


def get_file_modified_time(path: PathlibPath, tz: timezone = timezone) -> datetime:
    """
    Get file modified datetime

    :param tz:
    :param path: Path of file
    :return: File modification time, as reported by OS
    """
    return datetime.fromtimestamp(Path(path).stat().st_mtime_ns, tz=tz)


def dir_len(path: PathlibPath) -> int:
    return len(keys(path))


def path_exists(path: PathlibPath) -> bool:
    return Path(path).exists()
