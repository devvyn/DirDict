from datetime import timedelta
from io import BufferedWriter, BufferedReader
from os import PathLike
from typing import Tuple, Iterator, Mapping, Optional, Sequence, Dict, Union, Any, NoReturn

from storage.dirdict.functions import remove_base_path, keys, get, set_, del_, get_file_age, dir_len, \
    initialize_base_path, get_key_path, path_exists


def guard_string_type(o: Any, t=str) -> NoReturn:
    if isinstance(o, t):
        raise TypeError('Expected `str`, got %s', type(o))


class FileSystemWrapperDict:
    """
    This is a shallow implementation of a dictionary-like wrapper over a directory
    in the host file system; no sub-directories will be traversed or exposed, or created.

    Store bytes or str in dictionary style mapping, persisted on disk as
    user-accessible, discrete files, named by key and containing raw data.

    There may be collisions between keys due to limitations of the host OS file system, such as case insensitivity or
    forbidden characters. Collisions are not detected or reported.
    """

    def __init__(self, path, directory_mode=0x750, file_mode: int = 0o640, exist_ok: bool = True):
        initialize_base_path(path, mode=directory_mode, exist_ok=exist_ok)
        self.path = path
        self.directory_mode = directory_mode
        self.file_mode = file_mode
        self.exist_okay = exist_ok

    def __len__(self) -> int:
        """
        :return: Number of files in the storage path
        """
        return dir_len(self.path)

    def __getitem__(self, key: str) -> bytes:
        """
        Get file contents from disk, if file matching key exists

        :raises: Union[KeyError, TypeError]
        """
        guard_string_type(key)
        try:
            return get(self.get_key_path(key))
        except OSError:
            raise KeyError(key)

    def __setitem__(self, key: str, value: bytes) -> None:
        """
        Create or update file on disk

        :param key: Key name
        :param value: Data to store in file corresponding to key name
        """
        guard_string_type(key)
        set_(self.get_key_path(key), value)

    def __delitem__(self, key: str) -> None:
        """
        Delete a file from disk that corresponds to the `key`, if it exists

        :raises: KeyError
        """
        guard_string_type(key)
        del_(self.get_key_path(key))

    def __iter__(self) -> Iterator[Union[bytes, str]]:
        """
        As with dict.__iter__

        :return: Iterator over keys
        """
        return iter(self.keys())

    def values(self):
        """

        :return: Iterator over values; same as d.values() for dict
        """
        return iter(self.get(key) for key in self.keys())

    def keys(self):
        """
        As with dict.keys()

        :return: Iterable of keys
        """
        return keys(self.path)

    def __contains__(self, key: str) -> bool:
        """
        Containment test

        :param key: Key name
        :return: True if key is a member of the set of keys
        """
        guard_string_type(key)
        return path_exists(self.get_key_path(key))
        
    def items(self) -> Iterator[Tuple[Union[bytes, str], Union[BufferedWriter, BufferedReader]]]:
        """
        As with dict.items()

        :return: Iterable of key and value pairs; could be passed to a dict() constructor
        """
        return zip(self.keys(), self.values())

    def get(self, key: str, default: Any = None) -> Union[bytes, Any]:
        """
        As with `dict.get(key, default)`, return corresponding value if key exists but do not raise KeyError

        :param default: Defaults to None
        :param key: Key name
        :return: Contents of file that corresponds with `key`, or `default`
        """
        guard_string_type(key)
        try:
            return get(self.get_key_path(key))
        except KeyError:
            return default

    def clear(self) -> None:
        """
        As with remove_base_path(), remove the directory's contents, but re-initialize afterward

        """
        remove_base_path(self.path)
        initialize_base_path(self.path, mode=self.directory_mode, exist_ok=False)

    def setdefault(self, key: AnyStr, default: Optional[AnyStr] = None) -> AnyStr:
        """
        As with dict: d.setdefault(...)

        :param key: Key name
        :param default: Value to set if key not already set
        :return: Stored value if one exists, `default` if not
        """
        path = self.get_key_path(key)
        return get(path) or set_(path, default) and default

    def popitem(self) -> Tuple[AnyStr, AnyStr]:
        raise NotImplementedError()

    def pop(self, key: AnyStr, **kwargs) -> AnyStr:
        """There's no way to sanely choose a "last" item or "top of stack" in all operating systems and file systems,
        so `pop()` would not be consistently deterministic. """
        raise NotImplementedError()

    def copy(self) -> Dict[Union[bytes, str], Union[BufferedWriter, BufferedReader]]:
        """
        Shallow copy, as with dict.copy()

        :return: Dictionary representing file names and contents of directory, excluding sub-directories
        """
        return dict(self.items())

    def update(self, iterable: Mapping[AnyStr, AnyStr], **kwargs: AnyStr) -> None:
        """
        Write all items to disk, even if they already exist, and are identical.
        This means the modified date may be updated by the OS

        :param iterable: As with `dict`
        :param kwargs: As with `dict`
        """
        for (k, v) in dict(iterable.items() | kwargs.items()):
            self.__setitem__(k, v)

    def get_key_path(self, key: Union[bytes, str, PathLike]) -> str:
        """
        Combine this instance's initialized path with the normalized file name according to host OS's path style

        :param key: The key name which corresponds with a file name in storage
        :return: The absolute path to the file corresponding with `key`
        """
        guard_string_type(key)
        return get_key_path(self.path, key)

    @staticmethod
    def fromkeys(seq: Sequence[AnyStr]) -> Dict[AnyStr, AnyStr]:
        raise NotImplementedError()  # @todo implement fromkeys, because this could be useful for populating a directory


class TTLCache(FileSystemWrapperDict):
    def __init__(self, path: AnyStr, weeks: int = 0, days: int = 0, hours: int = 0, minutes: int = 15,
                 seconds: int = 0, milliseconds: int = 0, microseconds: int = 0, **kwargs):
        """
        Initialize a FileSystemWrapperDict with a time to live cache mechanism, with TTL set according to
        `days`, `hours`, `minutes`, `seconds`, etc.

        Default TTL is 15 minutes.

        :param days:
        :param seconds:
        :param microseconds:
        :param milliseconds:
        :param minutes: Default = 15
        :param hours:
        :param weeks:
        :param kwargs: Passed to superclass constructor
        """
        super().__init__(path, **kwargs)
        timedelta_args = dict(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds,
                              minutes=minutes, hours=hours, weeks=weeks)
        self.ttl_interval = timedelta(**timedelta_args)

    def get(self, key: AnyStr, default: T = None) -> Union[BufferedWriter, BufferedReader, T]:
        """
        Like standard dictionary `get()`, but guarded for freshness.
        Keys self destruct on attempted access when expired.

        :param key:
        :param default: Returned if key does not exist or has expired
        :return: Value stored at `key`, or `default`
        """
        if not self.is_fresh(key):
            del self[key]
            if default is None:
                raise KeyError(key)
        return super().get(key, default)

    def is_fresh(self, key: AnyStr) -> bool:
        return self.ttl_interval > get_file_age(get_key_path(key))

    def __getitem__(self, key: ) ->:
        guard_string_type(key)
        return self.get(key)


class CachingWebProxy(TTLCache):
    """
    When key not found, fetch from internet as URL, then cache and return
    """
