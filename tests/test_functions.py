"""
Unit tests for dirdict.functions module.

Tests the low-level filesystem operations that back DirDict.
"""
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from dirdict.functions import (
    initialize_base_path,
    remove_base_path,
    keys,
    get,
    set_,
    del_,
    get_key_path,
    get_file_age,
    get_file_modified_time,
    dir_len,
    path_exists,
)


class TestInitializeBasePath:
    """Tests for initialize_base_path()"""

    def test_creates_directory(self, tmp_path):
        new_dir = tmp_path / "new_storage"
        assert not new_dir.exists()
        initialize_base_path(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_creates_nested_directories(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c"
        initialize_base_path(nested, parents=True)
        assert nested.exists()

    def test_exist_ok_true_allows_existing(self, tmp_path):
        existing = tmp_path / "existing"
        existing.mkdir()
        # Should not raise
        initialize_base_path(existing, exist_ok=True)
        assert existing.exists()

    def test_exist_ok_false_raises_on_existing(self, tmp_path):
        existing = tmp_path / "existing"
        existing.mkdir()
        with pytest.raises(FileExistsError):
            initialize_base_path(existing, exist_ok=False)

    def test_applies_mode(self, tmp_path):
        new_dir = tmp_path / "with_mode"
        initialize_base_path(new_dir, mode=0o700)
        assert new_dir.exists()
        # Check mode (masking off file type bits)
        actual_mode = new_dir.stat().st_mode & 0o777
        # Note: umask may affect this, so we check it's at least as restrictive
        assert actual_mode <= 0o700


class TestRemoveBasePath:
    """Tests for remove_base_path()"""

    def test_removes_empty_directory(self, tmp_path):
        target = tmp_path / "to_remove"
        target.mkdir()
        remove_base_path(target)
        assert not target.exists()

    def test_removes_directory_with_files(self, tmp_path):
        target = tmp_path / "to_remove"
        target.mkdir()
        (target / "file1.txt").write_bytes(b"content1")
        (target / "file2.txt").write_bytes(b"content2")
        remove_base_path(target)
        assert not target.exists()

    def test_raises_on_nonexistent(self, tmp_path):
        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError):
            remove_base_path(nonexistent)


class TestKeys:
    """Tests for keys()"""

    def test_empty_directory_returns_empty_set(self, tmp_path):
        result = keys(tmp_path)
        assert result == set()
        assert isinstance(result, set)

    def test_returns_filenames_as_strings(self, tmp_path):
        (tmp_path / "file1.txt").write_bytes(b"a")
        (tmp_path / "file2.txt").write_bytes(b"b")
        result = keys(tmp_path)
        assert result == {"file1.txt", "file2.txt"}
        # Verify they're strings, not Path objects
        for key in result:
            assert isinstance(key, str)

    def test_raises_on_nonexistent_directory(self, tmp_path):
        nonexistent = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError):
            keys(nonexistent)


class TestGetAndSet:
    """Tests for get() and set_()"""

    def test_set_creates_file(self, tmp_path):
        filepath = tmp_path / "newfile.txt"
        set_(filepath, b"hello world")
        assert filepath.exists()

    def test_get_reads_file(self, tmp_path):
        filepath = tmp_path / "existing.txt"
        filepath.write_bytes(b"test content")
        result = get(filepath)
        assert result == b"test content"

    def test_set_overwrites_existing(self, tmp_path):
        filepath = tmp_path / "file.txt"
        set_(filepath, b"original")
        set_(filepath, b"updated")
        assert get(filepath) == b"updated"

    def test_get_raises_on_nonexistent(self, tmp_path):
        filepath = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            get(filepath)

    def test_set_applies_mode(self, tmp_path):
        filepath = tmp_path / "with_mode.txt"
        set_(filepath, b"content", mode=0o600)
        actual_mode = filepath.stat().st_mode & 0o777
        # umask may affect, but should be restrictive
        assert actual_mode <= 0o640

    def test_handles_binary_data(self, tmp_path):
        filepath = tmp_path / "binary.bin"
        binary_data = bytes(range(256))
        set_(filepath, binary_data)
        assert get(filepath) == binary_data

    def test_handles_empty_content(self, tmp_path):
        filepath = tmp_path / "empty.txt"
        set_(filepath, b"")
        assert get(filepath) == b""


class TestDel:
    """Tests for del_()"""

    def test_deletes_existing_file(self, tmp_path):
        filepath = tmp_path / "to_delete.txt"
        filepath.write_bytes(b"content")
        del_(filepath)
        assert not filepath.exists()

    def test_raises_on_nonexistent(self, tmp_path):
        filepath = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            del_(filepath)


class TestGetKeyPath:
    """Tests for get_key_path()"""

    def test_combines_base_and_key(self, tmp_path):
        result = get_key_path(tmp_path, "mykey.txt")
        assert result == tmp_path / "mykey.txt"

    def test_returns_path_object(self, tmp_path):
        result = get_key_path(tmp_path, "key")
        assert isinstance(result, Path)


class TestFileAge:
    """Tests for get_file_age() and get_file_modified_time()"""

    def test_get_file_modified_time_returns_datetime(self, tmp_path):
        filepath = tmp_path / "test.txt"
        filepath.write_bytes(b"content")
        result = get_file_modified_time(filepath)
        assert isinstance(result, datetime)

    def test_get_file_age_returns_positive_timedelta(self, tmp_path):
        filepath = tmp_path / "test.txt"
        filepath.write_bytes(b"content")
        # Small sleep to ensure file has some age
        time.sleep(0.01)
        age = get_file_age(filepath)
        assert isinstance(age, timedelta)
        assert age.total_seconds() >= 0  # Age should be positive

    def test_get_file_age_with_relative_to(self, tmp_path):
        filepath = tmp_path / "test.txt"
        filepath.write_bytes(b"content")
        mtime = get_file_modified_time(filepath)
        # Ask for age relative to 1 hour after file was modified
        future = mtime + timedelta(hours=1)
        age = get_file_age(filepath, relative_to=future)
        # Age should be approximately 1 hour
        assert 3500 < age.total_seconds() < 3700

    def test_raises_on_nonexistent_file(self, tmp_path):
        filepath = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            get_file_modified_time(filepath)


class TestDirLen:
    """Tests for dir_len()"""

    def test_empty_directory(self, tmp_path):
        assert dir_len(tmp_path) == 0

    def test_counts_files(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"a")
        (tmp_path / "b.txt").write_bytes(b"b")
        (tmp_path / "c.txt").write_bytes(b"c")
        assert dir_len(tmp_path) == 3


class TestPathExists:
    """Tests for path_exists()"""

    def test_existing_file(self, tmp_path):
        filepath = tmp_path / "exists.txt"
        filepath.write_bytes(b"content")
        assert path_exists(filepath) is True

    def test_existing_directory(self, tmp_path):
        assert path_exists(tmp_path) is True

    def test_nonexistent(self, tmp_path):
        assert path_exists(tmp_path / "nope") is False
