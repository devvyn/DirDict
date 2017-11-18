from datetime import timedelta
from functools import partial
from typing import Tuple, Iterator, List, Mapping, Optional, Sequence, Dict

import storage.file_system.file_fn
from storage.file_system.types import BytesOrText, BufferedIO


class FileSystemWrapperDict:
    def __init__(self, path, directory_mode=0x750, file_mode: int = 0o640, exist_ok: bool = True):
        storage.file_system.file_fn.initialize_base_path(path, mode=directory_mode, exist_ok=exist_ok)
        self.path = path
        self.directory_mode = directory_mode
        self.file_mode = file_mode
        self.exist_okay = exist_ok
        self.get_key_path = partial(storage.file_system.file_fn.get_key_path, base_path=self.path)

    @staticmethod
    def __guard_type(o, t):
        if not isinstance(o, t):
            raise TypeError('Expected %s, got %s', t, type(o))

    __guard_type_text = partial(__guard_type, t=BytesOrText)

    def __len__(self) -> int:
        """
        :return: Number of files in the storage path
        """
        return storage.file_system.file_fn.dir_len(self.path)

    def __getitem__(self, key: BytesOrText) -> BufferedIO:
        """
        Get file contents from disk, if file matching key exists

        :raises: Union[KeyError, TypeError]
        """
        self.__guard_type_text(key)
        try:
            return storage.file_system.file_fn.get(self.get_key_path(key))
        except OSError:
            raise KeyError(key)

    def __setitem__(self, key: BytesOrText, value: BytesOrText) -> None:
        """
        Create or update file on disk

        :param key: Key name
        :param value: Data to store in file corresponding to key name
        """
        self.__guard_type_text(key)
        storage.file_system.file_fn.set_(self.get_key_path(key), value)

    def __delitem__(self, key: BytesOrText) -> None:
        """
        Delete a file from disk that corresponds to the `key`, if it exists

        :raises: KeyError
        """
        self.__guard_type_text(key)
        storage.file_system.file_fn.del_(self.get_key_path(key))

    def __iter__(self) -> Iterator[BytesOrText]:
        """
        As with dict.__iter__

        :return: Iterator over keys
        """
        return iter(self.keys())

    def values(self) -> Iterator[BufferedIO]:
        """

        :return: Iterator over values; same as d.values() for dict
        """
        return iter(self.get(file_name) for file_name in self.keys())

    def keys(self) -> List[BytesOrText]:
        """
        As with dict.keys()

        :return: Iterable of keys
        """
        # noinspection PyTypeChecker
        return storage.file_system.file_fn.keys(self.path)

    def __contains__(self, key: BytesOrText) -> bool:
        """
        Containment test

        :param key: Key name
        :return: True if k is a member of the set of keys
        """
        return key in self.keys()

    def items(self) -> Iterator[Tuple[BytesOrText, BytesOrText]]:
        """
        As with dict.items()

        :return: Iterable of key and value pairs; could be passed to a dict() constructor
        """
        # noinspection PyTypeChecker
        return zip(self.keys(), self.values())

    def get(self, key: BytesOrText, default: BytesOrText = None) -> BufferedIO:
        """
        As with dict.get(...)

        :param default:
        :param key: Key name
        :return: Contents of file that corresponds with `key`
        """
        try:
            return storage.file_system.file_fn.get(self.get_key_path(key))
        except KeyError:
            if default is not None:
                return default
            raise

    def clear(self) -> None:
        """
        As with remove_base_path(), remove the directory's contents, but re-initialize afterward

        :param mode: Directory permissions passed to OS
        """
        storage.file_system.file_fn.remove_base_path(self.path)
        storage.file_system.file_fn.initialize_base_path(self.path, mode=self.directory_mode, exist_ok=False)

    def setdefault(self, path: BytesOrText, default: Optional[BytesOrText] = None) -> BytesOrText:
        """
        As with dict: d.setdefault(...)

        :param path: Key name
        :param default: Value to set if key not already set
        :return: Stored value if one exists, `default` if not
        """
        return storage.file_system.file_fn.get(path) or storage.file_system.file_fn.set_(path, default) and default

    def popitem(self) -> Tuple[BytesOrText, BytesOrText]:
        raise NotImplementedError()

    def pop(self, key: BytesOrText, **kwargs) -> BytesOrText:
        """There's no way to sanely choose a "last" item or "top of stack" in all operating systems and file systems,
        so `pop()` would not be consistently deterministic. """
        raise NotImplementedError()

    def copy(self) -> Dict[BytesOrText, BytesOrText]:
        """
        Shallow copy, as with dict.copy()

        :return: Dictionary representing file names and contents of directory, excluding sub-directories
        """
        return dict(self.items())

    def update(self, iterable: Mapping[BytesOrText, BytesOrText], **kwargs: BytesOrText) -> None:
        """
        Write all items to disk, even if they already exist, and are identical.
        This means the modified date may be updated by the OS

        :param iterable: As with `dict`
        :param kwargs: As with `dict`
        """
        for (k, v) in dict(iterable.items() | kwargs.items()):
            self.__setitem__(k, v)

    @staticmethod
    def fromkeys(seq: Sequence[BytesOrText]) -> Dict[BytesOrText, BytesOrText]:
        raise NotImplementedError()  # @todo implement fromkeys, because this could be useful for populating a directory


class TTLCache(FileSystemWrapperDict):
    """
    This is a shallow implementation of a dictionary-like wrapper over a directory
    in the host file system; no sub-directories will be traversed or exposed, or created.

    Store bytes or str in dictionary style mapping, persisted on disk as
    user-accessible, discrete files, named by key and containing raw data.

    There may be collisions between keys due to limitations of the host OS file system, such as case insensitivity or
    forbidden characters. Collisions are not detected or reported.
    """

    def __init__(self, path: BytesOrText, weeks: int = 0, days: int = 0, hours: int = 0, minutes: int = 15,
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

    def get(self, key: BytesOrText, default: BytesOrText = None) -> BufferedIO:
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

    def is_fresh(self, key: BytesOrText) -> bool:
        return self.ttl_interval > storage.file_system.file_fn.get_file_age(super().get_key_path(key))

    def __getitem__(self, key: BytesOrText) -> BufferedIO:
        return self.get(key)


class CachingWebProxy(TTLCache):
    """
    When key not found, fetch from internet as URL, then cache and return
    """
