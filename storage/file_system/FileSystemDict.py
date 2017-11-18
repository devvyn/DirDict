import os
from datetime import timedelta
from functools import partial
from typing import Tuple, Iterator, List, Mapping, Optional, Sequence, Dict

from storage.file_system import Text, BufferedIO
from storage.file_system.fn import init_directory, get_file, set_file, get_keys, remove_directory, delete_file


class FileSystemDict:
    """
    Store bytes or str in dictionary style mapping, persisted on disk as
    user-accessible, discrete files named by key and containing raw contents.

    This is a shallow implementation of a dictionary-like wrapper over a directory
    in the host file system; no sub-directories will be traversed or exposed, or created.
    """

    @staticmethod
    def __guard_type(o, t):
        if not isinstance(o, t):
            raise TypeError('Expected %s, got %s', t, type(o))

    __guard_type_text = partial(__guard_type, t=Text)

    def __init__(self, path: Text = os.getcwd(), directory_mode: int = 0o755, exist_ok: bool = True,
                 **timedelta_kwargs):
        """
        Create a new directory for storage, if it does not exist, then set it as the target for object operations

        :param path: Path to directory on OS file system
        :param directory_mode: File permissions on OS file system
        :param exist_ok: Suppress file exists error from OS
        """
        self.ttl_interval = timedelta(**timedelta_kwargs)
        init_directory(path, exist_ok=exist_ok)
        self.path = path

    def __len__(self) -> int:
        """
        :return: Number of files in the storage path
        """
        # @todo: move this to file system handling layer in fn
        return len(get_keys(self.path))

    def __getitem__(self, item: Text) -> BufferedIO:
        """
        Get file contents from disk, if file matching key exists

        :raises: Union[KeyError, TypeError]
        """
        self.__guard_type_text(item)
        return get_file(key=item, path=self.path)

    def __setitem__(self, k: Text, v: Text) -> None:
        """
        Create or update file on disk

        :param k: Key name
        :param v: Data to store in file corresponding to key name
        """
        self.__guard_type_text(k)
        set_file(k, v)

    def __delitem__(self, key: Text) -> None:
        """
        Delete a file from disk that corresponds to the `key`, if it exists

        :raises: KeyError
        """
        self.__guard_type_text(key)
        delete_file(key)

    def __iter__(self) -> Iterator[Text]:
        """
        As with dict.__iter__

        :return: Iterator over keys
        """
        return iter(self.keys())

    def __contains__(self, k: Text) -> bool:
        """
        Containment test

        :param k: Key name
        :return: True if k is a member of the set of keys
        """
        return k in self.keys()

    def keys(self) -> List[Text]:
        """
        As with dict.keys()

        :return: Iterable of keys
        """
        return get_keys(self.path)

    def values(self) -> Iterator[BufferedIO]:
        """

        :return: Iterator over values; same as d.values() for dict
        """
        return iter(self.get(file_name, ) for file_name in self.keys())

    def items(self) -> Iterator[Tuple[Text, Text]]:
        """
        As with dict.items()

        :return: Iterable of key and value pairs; could be passed to a dict() constructor
        """
        # noinspection PyTypeChecker
        return zip(self.keys(), self.values())

    def get(self, key: Text,  **kwargs) -> BufferedIO:
        """
        As with dict.get(...)

        :param ttl_interval: Maximum acceptable file age
        :param key: Key name
        :return: Contents of file that corresponds with `key`
        """
        if ttl_interval is not None:
            interval = ttl_interval
        else:
            interval = self.ttl_interval
        return get_file(key=key, path=self.path)

    def clear(self, mode: int = 0o750) -> None:
        """
        As with remove_directory(), remove the directory's contents, but re-initialize afterward

        :param mode: Directory permissions passed to OS
        """
        remove_directory(self.path)
        init_directory(self.path, mode=mode, exist_ok=False)

    def setdefault(self, k: Text, default: Optional[Text] = None) -> Text:
        """
        As with dict: d.setdefault(...)

        :param k: Key name
        :param default: Value to set if key not already set
        :return: Stored value if one exists, `default` if not
        """
        return get_file(k, ttl_interval=self.ttl_interval) or set_file(k, default) and default

    def popitem(self) -> Tuple[Text, Text]:
        raise NotImplementedError()

    def pop(self, key: Text, **kwargs) -> Text:
        raise NotImplementedError()

    def copy(self) -> Dict[Text, Text]:
        """
        Shallow copy, as with dict.copy()

        :return: Dictionary representing file names and contents of directory, excluding sub-directories
        """
        return dict(self.items())

    def update(self, iterable: Mapping[Text, Text], **kwargs: Text) -> None:
        """
        Write all items to disk, even if they already exist, and are identical.
        This means the modified date may be updated by the OS

        :param iterable: As with `dict`
        :param kwargs: As with `dict`
        """
        for (k, v) in dict(iterable.items() | kwargs.items()):
            self.__setitem__(k, v)

    @staticmethod
    def fromkeys(seq: Sequence[Text]) -> Dict[Text, Text]:
        raise NotImplementedError()  # @todo implement fromkeys, because this could be useful for populating a directory
