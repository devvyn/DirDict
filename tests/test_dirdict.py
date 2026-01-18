"""
Unit tests for the DirDict class.

Tests the dictionary-like interface over filesystem storage.
"""
import pytest
from pathlib import Path

from dirdict import DirDict


class TestDirDictInit:
    """Tests for DirDict initialization"""

    def test_creates_directory(self, tmp_path):
        storage = tmp_path / "new_storage"
        dd = DirDict(storage)
        assert storage.exists()
        assert storage.is_dir()

    def test_accepts_existing_directory(self, tmp_path):
        storage = tmp_path / "existing"
        storage.mkdir()
        dd = DirDict(storage)  # Should not raise
        assert dd.path == storage

    def test_exist_ok_false_raises_on_existing(self, tmp_path):
        storage = tmp_path / "existing"
        storage.mkdir()
        with pytest.raises(FileExistsError):
            DirDict(storage, exist_ok=False)

    def test_stores_configuration(self, tmp_path):
        storage = tmp_path / "storage"
        dd = DirDict(storage, directory_mode=0o700, file_mode=0o600)
        assert dd.directory_mode == 0o700
        assert dd.file_mode == 0o600


class TestDirDictBasicOperations:
    """Tests for basic dict operations"""

    @pytest.fixture
    def dd(self, tmp_path):
        return DirDict(tmp_path / "storage")

    def test_setitem_creates_file(self, dd):
        dd["key1"] = b"value1"
        filepath = Path(dd.path) / "key1"
        assert filepath.exists()
        assert filepath.read_bytes() == b"value1"

    def test_getitem_reads_file(self, dd):
        dd["key1"] = b"value1"
        assert dd["key1"] == b"value1"

    def test_getitem_raises_keyerror_on_missing(self, dd):
        with pytest.raises(KeyError):
            _ = dd["nonexistent"]

    def test_delitem_removes_file(self, dd):
        dd["key1"] = b"value1"
        del dd["key1"]
        filepath = Path(dd.path) / "key1"
        assert not filepath.exists()

    def test_delitem_raises_keyerror_on_missing(self, dd):
        with pytest.raises(KeyError):
            del dd["nonexistent"]

    def test_len_counts_files(self, dd):
        assert len(dd) == 0
        dd["a"] = b"a"
        assert len(dd) == 1
        dd["b"] = b"b"
        assert len(dd) == 2
        del dd["a"]
        assert len(dd) == 1

    def test_contains_checks_existence(self, dd):
        assert "key1" not in dd
        dd["key1"] = b"value"
        assert "key1" in dd
        del dd["key1"]
        assert "key1" not in dd


class TestDirDictIteration:
    """Tests for iteration methods"""

    @pytest.fixture
    def populated_dd(self, tmp_path):
        dd = DirDict(tmp_path / "storage")
        dd["alpha"] = b"a"
        dd["beta"] = b"b"
        dd["gamma"] = b"c"
        return dd

    def test_iter_yields_keys(self, populated_dd):
        keys = set(populated_dd)
        assert keys == {"alpha", "beta", "gamma"}

    def test_keys_returns_set(self, populated_dd):
        keys = populated_dd.keys()
        assert isinstance(keys, set)
        assert keys == {"alpha", "beta", "gamma"}

    def test_values_yields_contents(self, populated_dd):
        values = set(populated_dd.values())
        assert values == {b"a", b"b", b"c"}

    def test_items_yields_pairs(self, populated_dd):
        items = dict(populated_dd.items())
        assert items == {"alpha": b"a", "beta": b"b", "gamma": b"c"}


class TestDirDictDictMethods:
    """Tests for dict-like methods"""

    @pytest.fixture
    def dd(self, tmp_path):
        return DirDict(tmp_path / "storage")

    def test_get_returns_value(self, dd):
        dd["key"] = b"value"
        assert dd.get("key") == b"value"

    def test_get_returns_default_on_missing(self, dd):
        assert dd.get("missing") is None
        assert dd.get("missing", b"default") == b"default"

    def test_setdefault_existing(self, dd):
        dd["key"] = b"original"
        result = dd.setdefault("key", b"default")
        assert result == b"original"
        assert dd["key"] == b"original"

    def test_setdefault_missing(self, dd):
        result = dd.setdefault("key", b"default")
        assert result == b"default"
        assert dd["key"] == b"default"

    def test_pop_removes_and_returns(self, dd):
        dd["key"] = b"value"
        result = dd.pop("key")
        assert result == b"value"
        assert "key" not in dd

    def test_pop_with_default(self, dd):
        result = dd.pop("missing", default=b"fallback")
        assert result == b"fallback"

    def test_pop_raises_without_default(self, dd):
        # Note: Original implementation raises TypeError with specific message format
        with pytest.raises(TypeError, match="Expected argument"):
            dd.pop("missing")

    def test_popitem_removes_arbitrary(self, dd):
        dd["key1"] = b"value1"
        dd["key2"] = b"value2"
        key, value = dd.popitem()
        assert key in {"key1", "key2"}
        assert key not in dd
        assert len(dd) == 1

    def test_popitem_empty_raises(self, dd):
        with pytest.raises(KeyError):
            dd.popitem()

    def test_clear_removes_all(self, dd):
        dd["a"] = b"a"
        dd["b"] = b"b"
        dd.clear()
        assert len(dd) == 0
        assert Path(dd.path).exists()  # Directory should still exist

    def test_update_from_dict(self, dd):
        dd.update({"a": b"1", "b": b"2"})
        assert dd["a"] == b"1"
        assert dd["b"] == b"2"

    def test_update_overwrites(self, dd):
        dd["a"] = b"original"
        dd.update({"a": b"updated"})
        assert dd["a"] == b"updated"


class TestDirDictCopy:
    """Tests for copy()"""

    def test_copy_returns_same_config(self, tmp_path):
        storage = tmp_path / "storage"
        dd = DirDict(storage, directory_mode=0o700, file_mode=0o600)
        dd["key"] = b"value"

        copy = dd.copy()
        assert copy.path == dd.path
        assert copy.directory_mode == dd.directory_mode
        assert copy.file_mode == dd.file_mode
        # They share the same underlying storage
        assert copy["key"] == b"value"


class TestDirDictFromkeys:
    """Tests for fromkeys()"""

    def test_fromkeys_creates_with_mapping(self, tmp_path):
        storage = tmp_path / "storage"
        dd = DirDict.fromkeys(storage, {"a": b"1", "b": b"2"})
        assert dd["a"] == b"1"
        assert dd["b"] == b"2"


class TestDirDictTypeGuards:
    """Tests for type validation"""

    @pytest.fixture
    def dd(self, tmp_path):
        return DirDict(tmp_path / "storage")

    def test_rejects_non_string_key_on_get(self, dd):
        with pytest.raises(TypeError):
            _ = dd[123]

    def test_rejects_non_string_key_on_set(self, dd):
        with pytest.raises(TypeError):
            dd[123] = b"value"

    def test_rejects_non_string_key_on_del(self, dd):
        with pytest.raises(TypeError):
            del dd[123]

    def test_rejects_non_string_key_on_contains(self, dd):
        with pytest.raises(TypeError):
            _ = 123 in dd

    def test_bytes_key_raises_typeerror(self, dd):
        # Note: While bytes are accepted by the type guard, pathlib.Path
        # on Python 3.11+ rejects bytes in path construction.
        # This is a known limitation - keys should be str.
        with pytest.raises(TypeError):
            dd[b"bytekey"] = b"value"


class TestDirDictEdgeCases:
    """Tests for edge cases and special scenarios"""

    @pytest.fixture
    def dd(self, tmp_path):
        return DirDict(tmp_path / "storage")

    def test_empty_value(self, dd):
        dd["empty"] = b""
        assert dd["empty"] == b""

    def test_binary_data(self, dd):
        binary = bytes(range(256))
        dd["binary"] = binary
        assert dd["binary"] == binary

    def test_unicode_key(self, dd):
        dd["unicode_\u00e9"] = b"value"
        assert dd["unicode_\u00e9"] == b"value"

    def test_key_with_extension(self, dd):
        dd["data.json"] = b'{"key": "value"}'
        assert dd["data.json"] == b'{"key": "value"}'

    def test_overwrite_preserves_only_new_value(self, dd):
        dd["key"] = b"first"
        dd["key"] = b"second"
        assert dd["key"] == b"second"
