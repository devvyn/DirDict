import os
from datetime import timedelta
from functools import partial
from typing import Tuple, Iterator, List, Mapping, Optional, Sequence, Dict

from storage.file_system.file_fn import init_directory, get, set_, values, remove_directory, del_, get_key_path
from storage.file_system.types import T, BufferedIO


class FileSystemWrapperDict:
    def __init__(self, path, directory_mode=0x750, exist_ok: bool = True):
        init_directory(path, mode=directory_mode, exist_ok=exist_ok)
        self.path = path

    @staticmethod
    def __guard_type(o, t):
        if not isinstance(o, t):
            raise TypeError('Expected %s, got %s', t, type(o))

    __guard_type_text = partial(__guard_type, t=T)

    def __len__(self) -> int:
        """
        :return: Number of files in the storage path
        """
        # @todo: move this to file system handling layer in fn
        return len(values(self.path))

    def __getitem__(self, item: T) -> BufferedIO:
        """
        Get file contents from disk, if file matching key exists

        :raises: Union[KeyError, TypeError]
        """
        self.__guard_type_text(item)
        return get(self.path)

    def __setitem__(self, key: T, value: T) -> None:
        """
        Create or update file on disk

        :param key: Key name
        :param value: Data to store in file corresponding to key name
        """
        self.__guard_type_text(key)
        set_(key, value)

    def __delitem__(self, key: T) -> None:
        """
        Delete a file from disk that corresponds to the `key`, if it exists

        :raises: KeyError
        """
        self.__guard_type_text(key)
        del_(key)

    def __iter__(self) -> Iterator[T]:
        """
        As with dict.__iter__

        :return: Iterator over keys
        """
        return iter(self.keys())

    def values(self) -> Iterator[BufferedIO]:
        """

        :return: Iterator over values; same as d.values() for dict
        """
        return iter(self.get(file_name, ) for file_name in self.keys())

    def keys(self) -> List[T]:
        """
        As with dict.keys()

        :return: Iterable of keys
        """
        # noinspection PyTypeChecker
        return values(self.path)

    def __contains__(self, key: T) -> bool:
        """
        Containment test

        :param key: Key name
        :return: True if k is a member of the set of keys
        """
        return key in self.keys()

    def items(self) -> Iterator[Tuple[T, T]]:
        """
        As with dict.items()

        :return: Iterable of key and value pairs; could be passed to a dict() constructor
        """
        # noinspection PyTypeChecker
        return zip(self.keys(), self.values())

    def get(self, key: T) -> BufferedIO:
        """
        As with dict.get(...)

        :param key: Key name
        :return: Contents of file that corresponds with `key`
        """
        return get(get_key_path(key))

    def clear(self, mode: int = 0o750) -> None:
        """
        As with remove_directory(), remove the directory's contents, but re-initialize afterward

        :param mode: Directory permissions passed to OS
        """
        remove_directory(self.path)
        init_directory(self.path, mode=mode, exist_ok=False)

    def setdefault(self, path: T, default: Optional[T] = None) -> T:
        """
        As with dict: d.setdefault(...)

        :param path: Key name
        :param default: Value to set if key not already set
        :return: Stored value if one exists, `default` if not
        """
        return get(path) or set_(path, default) and default

    def popitem(self) -> Tuple[T, T]:
        raise NotImplementedError()

    def pop(self, key: T, **kwargs) -> T:
        raise NotImplementedError()

    def copy(self) -> Dict[T, T]:
        """
        Shallow copy, as with dict.copy()

        :return: Dictionary representing file names and contents of directory, excluding sub-directories
        """
        return dict(self.items())

    def update(self, iterable: Mapping[T, T], **kwargs: T) -> None:
        """
        Write all items to disk, even if they already exist, and are identical.
        This means the modified date may be updated by the OS

        :param iterable: As with `dict`
        :param kwargs: As with `dict`
        """
        for (k, v) in dict(iterable.items() | kwargs.items()):
            self.__setitem__(k, v)

    @staticmethod
    def fromkeys(seq: Sequence[T]) -> Dict[T, T]:
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

    def __init__(self, path: T = os.getcwd(), directory_mode: int = 0o755, exist_ok: bool = True, **timedelta_kwargs):
        """
        Create a new directory for storage, if it does not exist, then set it as the target for object operations

        :param path: Path to directory on OS file system
        :param directory_mode: File permissions on OS file system
        :param exist_ok: Suppress file exists error from OS
        """
        super().__init__(path, directory_mode=directory_mode, exist_ok=exist_ok)
        self.ttl_interval = timedelta(**timedelta_kwargs)
