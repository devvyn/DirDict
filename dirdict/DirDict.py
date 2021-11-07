from datetime import timedelta
from pathlib import PurePath
from typing import Tuple, Iterator, Mapping, Sequence, Any, AnyStr, Set, Type

from dirdict.functions import remove_base_path, keys, get, set_, del_, get_file_age, dir_len, \
    initialize_base_path, get_key_path, path_exists, PathlibPath


def guard_string_type(o: Any, t: Type = (bytes, str)) -> None:
    """
    Raise exception if `o` is not a string compatible with Python dict keys, in imitation of the built in dict methods

    :param o: The reference to check
    :param t: The string type or tuple of types acceptable
    :raises: TypeError
    """
    if not isinstance(o, t):
        raise TypeError('Expected string, got', type(o))


def get_optional_argument(name: str = None, position: int = None, *args, **kwargs) -> Any:
    """
    Return a named or positional argument if found in given args or kwargs, otherwise raise TypeError;
    named arguments checked before positional arguments

    :param name: Key into kwargs at which to check for expected argument
    :param position: Index into args at which to check for expected argument
    :param args: positional arguments
    :param kwargs: keyword arguments
    :return: Value of argument, if found
    :raises: TypeError
    """
    if name in kwargs:
        return kwargs[name]
    elif len(args) >= position:
        return args[position]
    if name is not None:
        raise TypeError(f"Expected argument '{name}' not found")
    else:
        raise TypeError(f"Expected at least {position + 1} arguments, got {len(args)}")


class DirDict:
    """
    This is a shallow implementation of a dictionary-like wrapper over a directory
    in the host file system; no sub-directories will be traversed or exposed, or created.

    Store bytes or str in dictionary style mapping, persisted on disk as
    user-accessible, discrete files, named by key and containing raw data.

    There may be collisions between keys due to limitations of the host OS file system, such as case insensitivity or
    forbidden characters. Collisions are not detected or reported.
    """

    def __init__(self, path: PathlibPath, directory_mode: int = 0x750, file_mode: int = 0o640,
                 exist_ok: bool = True) -> None:
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

    def __getitem__(self, key: AnyStr) -> bytes:
        """
        Get file contents from disk, if file matching key exists

        :raises: Union[KeyError, TypeError]
        """
        guard_string_type(key)
        try:
            return get(self.get_key_path(key))
        except OSError:
            raise KeyError(key)

    def __setitem__(self, key: AnyStr, value: bytes) -> None:
        """
        Create or update file on disk

        :param key: Key name
        :param value: Data to store in file corresponding to key name
        """
        guard_string_type(key)
        set_(self.get_key_path(key), value, mode=self.file_mode)

    def __delitem__(self, key: AnyStr) -> None:
        """
        Delete a file from disk that corresponds to the `key`, if it exists

        :raises: KeyError
        """
        guard_string_type(key)
        if not key in self:
            raise KeyError(key)
        del_(self.get_key_path(key))

    def __iter__(self) -> Iterator[str]:
        """
        As with dict.__iter__

        :return: Iterator over keys
        """
        return iter(self.keys())

    def values(self) -> Iterator[bytes]:
        """

        :return: Iterator over values; same as d.values() for dict
        """
        return iter(self[key] for key in self.keys())

    def keys(self) -> Set[str]:
        """
        Get the names of all keys in this instance

        :return: Set of keys
        """
        return keys(self.path)

    def __contains__(self, key: AnyStr) -> bool:
        """
        Containment test

        :param key: Key name
        :return: True if key is a member of the set of keys
        """
        guard_string_type(key)
        return path_exists(self.get_key_path(key))

    def items(self) -> Iterator[Tuple[str, Any]]:
        """
        Get the set of tuples

        :return: Iterable of key and value pairs; could be passed to a dict() constructor
        """
        return iter((key, self[key]) for key in self.keys())

    def get(self, key: AnyStr, default: Any = None) -> Any:
        """
        As with `dict.get(key, default)`, return corresponding value if key exists, or `default` if it doesn't

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

    def setdefault(self, key: AnyStr, default: Any = None) -> Any:
        """
        If key is in the instance, return its value. If not, insert key with a value of default and return default.

        :param key: Key name to retrieve
        :param default: Value to set if key not already set
        :return: Stored value if one exists, `default` if not
        """
        guard_string_type(key)
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return default  # @todo consider casting to bytes or fetching from file instead of passing through

    def popitem(self) -> Tuple[str, bytes]:
        """
        Remove and return an arbitrary (key, value) pair from the instance

        :return: (key, value) of popped item
        """
        key = self.keys().pop()
        item = (key, self[key])
        del self[key]  # @todo test whether file contents are still returned after file deletion
        return item

    def pop(self, key: AnyStr, *args, **kwargs) -> Any:
        """
        As with `dict.pop()`, lookup key and return its value; if key not found, return `default` if provided, otherwise
        raise KeyError

        :param key: Key to look up
        :param default: Value to return if key not found
        :return: Value or `default`
        :raises: KeyError
        """
        guard_string_type(key)
        try:
            value = self[key]
        except KeyError:
            default = get_optional_argument(name='default', position=0, *args, **kwargs)
            return default
        del self[key]  # @todo test whether file contents are still returned after file deletion
        return value

    def copy(self) -> 'DirDict':
        """
        Shallow copy, similar to dict.copy(), except keys don't actually need to be copied

        :return: New instance of this class with same configuration
        """
        return DirDict(self.path, directory_mode=self.directory_mode, file_mode=self.file_mode,
                       exist_ok=self.exist_okay)

    def update(self, iterable: Mapping[AnyStr, AnyStr], **kwargs: AnyStr) -> None:
        """
        Write all items to disk, even if they already exist, and are identical.
        This means the modified date may be updated by the OS

        :param iterable: As with `dict`
        :param kwargs: As with `dict`
        """
        for (k, v) in dict(iterable.items() | kwargs.items()):
            self.__setitem__(k, v)

    def get_key_path(self, key: PathlibPath) -> PurePath:
        """
        Combine this instance's initialized path with the normalized file name according to host OS's path style

        :param key: The key name which corresponds with a file name in storage
        :return: The absolute path to the file corresponding with `key`
        """
        guard_string_type(key)
        return get_key_path(self.path, key)

    @staticmethod
    def fromkeys(path: PathlibPath, seq: Sequence[AnyStr], **options) -> 'DirDict':
        """
        As with `dict.fromkeys()`, return a new instance with all the given key-value pairs

        :param path: Passed to `DirDict.__init__(...)`
        :param seq: Passed to `update(...)` method of instance
        :param options: Passed to `DirDict.__init__(...)`
        :return: Instance of DirDict with keys updated
        """
        o = DirDict(path, **options)
        o.update(seq)
        return o


class TTLCache(DirDict):
    """
    Time to live cache for files, with lazy deletion; actions that check or read from expired keys trigger deletion

    NOTE: Take care to observe the timezone used by the file system and the OS, so that files expire when they should.
    """

    def __init__(self, path: PathlibPath, ttl_interval: timedelta = None, **kwargs):
        """
        Initialize a DirDict with a time to live cache mechanism, with TTL set according to `ttl_interval`.

        :param ttl_interval: Time interval for item expiry
        :param kwargs: Passed to superclass constructor
        """
        super().__init__(path, **kwargs)
        self.ttl_interval = timedelta(hours=12) if ttl_interval is None else ttl_interval

    def __getitem__(self, key: AnyStr) -> bytes:
        guard_string_type(key)
        self.guard_expired(key)
        return super().__getitem__(key)

    def __len__(self) -> int:
        self.flush_expired_keys()
        return super().__len__()

    def __delitem__(self, key: AnyStr) -> None:
        """
        Delete key if it it's not expired, otherwise raise KeyError; if key exists and it's expired, it will
        also be deleted before the KeyError is raised

        :param key: Key to delete
        :raises: KeyError
        """
        guard_string_type(key)
        self.guard_expired(key)
        super().__delitem__(key)

    def __contains__(self, key: str) -> bool:
        """
        Check if key exists and is not expired; delete expired key
        :param key:
        :return:
        """
        guard_string_type(key)
        try:
            self.guard_expired(key)
            return True
        except:
            return False

    def keys(self) -> Set[str]:
        """
        Return the set of keys that aren't expired; delete expired keys

        :return: Valid keys
        """
        # for performance, get keys only once, rather than flushing and getting again
        unverified_keys = {*super().keys()}
        verified_keys = unverified_keys - self.flush_expired_keys(unverified_keys)
        return verified_keys

    def get(self, key: AnyStr, default: Any = None) -> bytes:
        """
        Like standard dictionary `get()`, but with timed expiry.
        Keys self destruct upon attempted access after they've expired.

        :param key:
        :param default: Returned if key does not exist or has expired
        :return: Value stored at `key`, or `default`
        """
        self.guard_expired(key)
        return super().get(key, default)

    def is_expired(self, key: AnyStr) -> bool:
        """
        Check if key is expired

        :param key:
        :return: True if key age is greater than `ttl_interval`
        :raises: KeyError
        """
        try:
            return self.ttl_interval < get_file_age(get_key_path(self.path, key))
        except OSError:
            raise KeyError(key)

    def guard_expired(self, key: AnyStr) -> None:
        """
        Remove key if expired

        :param key: Key to check
        :raises: KeyError
        """
        if self.is_expired(key):
            super().__delitem__(key)

    def flush_expired_keys(self, key_set: Set[AnyStr] = None) -> Set[AnyStr]:
        unverified_keys = key_set if key_set is not None else super().keys()
        expired_keys = {key for key in unverified_keys if self.is_expired(key)}
        for key in expired_keys:
            super().__delitem__(key)
        return expired_keys


class CachingWebProxy(TTLCache):
    """
    When key not found, fetch from internet as URL, then cache and return
    """

    def __init__(self, path: PathlibPath, ttl_interval: timedelta = None, **kwargs):
        raise NotImplementedError()
