"""
Unit tests for the TTLCache class.

Tests the time-to-live cache functionality.
"""
import os
import time
from datetime import timedelta
from pathlib import Path

import pytest

from dirdict import TTLCache


class TestTTLCacheInit:
    """Tests for TTLCache initialization"""

    def test_default_ttl(self, tmp_path):
        cache = TTLCache(tmp_path / "cache")
        assert cache.ttl_interval == timedelta(hours=12)

    def test_custom_ttl(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(minutes=30))
        assert cache.ttl_interval == timedelta(minutes=30)

    def test_inherits_dirdict_behavior(self, tmp_path):
        storage = tmp_path / "cache"
        cache = TTLCache(storage)
        assert storage.exists()


class TestTTLCacheExpiration:
    """Tests for TTL expiration behavior"""

    @pytest.fixture
    def cache(self, tmp_path):
        # Very short TTL for testing
        return TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))

    def test_fresh_key_accessible(self, cache):
        cache["key"] = b"value"
        assert cache["key"] == b"value"

    def test_expired_key_raises_keyerror(self, cache):
        cache["key"] = b"value"
        time.sleep(0.15)  # Wait for expiration
        with pytest.raises(KeyError):
            _ = cache["key"]

    def test_expired_key_deleted_from_disk(self, cache):
        cache["key"] = b"value"
        filepath = Path(cache.path) / "key"
        assert filepath.exists()
        time.sleep(0.15)
        try:
            _ = cache["key"]
        except KeyError:
            pass
        assert not filepath.exists()

    def test_expired_key_not_in_keys(self, cache):
        cache["key"] = b"value"
        assert "key" in cache.keys()
        time.sleep(0.15)
        assert "key" not in cache.keys()

    def test_expired_key_not_in_contains(self, cache):
        cache["key"] = b"value"
        assert "key" in cache
        time.sleep(0.15)
        assert "key" not in cache


class TestTTLCacheLen:
    """Tests for len() with expiration"""

    def test_len_excludes_expired(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))
        cache["fresh"] = b"value"

        # Manually create an old file
        old_file = Path(cache.path) / "old"
        old_file.write_bytes(b"old_value")
        # Set mtime to the past
        old_mtime = time.time() - 1  # 1 second ago
        os.utime(old_file, (old_mtime, old_mtime))

        # Should only count the fresh one
        assert len(cache) == 1


class TestTTLCacheGet:
    """Tests for get() with expiration"""

    @pytest.fixture
    def cache(self, tmp_path):
        return TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))

    def test_get_fresh_returns_value(self, cache):
        cache["key"] = b"value"
        assert cache.get("key") == b"value"

    def test_get_expired_raises_keyerror(self, cache):
        cache["key"] = b"value"
        time.sleep(0.15)
        # Note: TTLCache.get() raises KeyError for expired keys
        # (differs from dict.get() behavior, but consistent with TTL semantics)
        with pytest.raises(KeyError):
            cache.get("key")


class TestTTLCacheIsExpired:
    """Tests for is_expired() method"""

    def test_fresh_not_expired(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(hours=1))
        cache["key"] = b"value"
        assert cache.is_expired("key") is False

    def test_old_is_expired(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))
        cache["key"] = b"value"
        time.sleep(0.15)
        assert cache.is_expired("key") is True

    def test_nonexistent_raises_keyerror(self, tmp_path):
        cache = TTLCache(tmp_path / "cache")
        with pytest.raises(KeyError):
            cache.is_expired("nonexistent")


class TestTTLCacheFlushExpiredKeys:
    """Tests for flush_expired_keys() method"""

    def test_flush_removes_expired_files(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))

        # Create fresh key
        cache["fresh"] = b"fresh_value"

        # Manually create old file
        old_file = Path(cache.path) / "old"
        old_file.write_bytes(b"old_value")
        old_mtime = time.time() - 1
        os.utime(old_file, (old_mtime, old_mtime))

        expired = cache.flush_expired_keys()
        assert "old" in expired
        assert "fresh" not in expired
        assert not old_file.exists()
        assert (Path(cache.path) / "fresh").exists()

    def test_flush_returns_expired_keys(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))
        cache["key"] = b"value"
        time.sleep(0.15)

        expired = cache.flush_expired_keys()
        assert "key" in expired


class TestTTLCacheDelItem:
    """Tests for __delitem__ with expiration"""

    def test_delete_fresh_key(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(hours=1))
        cache["key"] = b"value"
        del cache["key"]
        assert "key" not in cache

    def test_delete_expired_key_raises(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=0.1))
        cache["key"] = b"value"
        time.sleep(0.15)
        with pytest.raises(KeyError):
            del cache["key"]


class TestTTLCacheWithManualMtime:
    """Tests using manually set mtimes for deterministic testing"""

    def test_key_just_under_ttl_accessible(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=10))
        cache["key"] = b"value"

        # Set mtime to 9 seconds ago (just under TTL)
        filepath = Path(cache.path) / "key"
        past_time = time.time() - 9
        os.utime(filepath, (past_time, past_time))

        assert cache["key"] == b"value"

    def test_key_just_over_ttl_expired(self, tmp_path):
        cache = TTLCache(tmp_path / "cache", ttl_interval=timedelta(seconds=10))
        cache["key"] = b"value"

        # Set mtime to 11 seconds ago (just over TTL)
        filepath = Path(cache.path) / "key"
        past_time = time.time() - 11
        os.utime(filepath, (past_time, past_time))

        with pytest.raises(KeyError):
            _ = cache["key"]
