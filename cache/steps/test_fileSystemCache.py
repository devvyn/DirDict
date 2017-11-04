import os.path
from os import chdir, listdir

from pytest_bdd import given, scenarios, parsers, when, then

from cache.file_system import FileSystemCache

scenarios('../features')


@given('a temporary working directory')
def working_directory(tmpdir):
    chdir(tmpdir)
    return tmpdir


@given(parsers.parse("a path '{cache_directory_name}'"))
def cache_path(working_directory, cache_directory_name):
    return os.path.join(working_directory, cache_directory_name)


@given(parsers.parse('the time to live is {ttl_seconds:d} seconds'))
def get_ttl_seconds(ttl_seconds):
    return ttl_seconds


@given('the cache path does not exist')
def cache_path_not_exists(cache_path):
    assert os.path.exists(cache_path) is False


@when('the cache path exists')
@then('the cache path exists')
def cache_path_exists(cache_path):
    assert os.path.exists(cache_path) is True


@then('the cache path points to a directory')
def cache_path_is_directory(cache_path):
    assert os.path.isdir(cache_path)


@when('cache directory is empty')
@then('cache directory is empty')
def cache_directory_is_empty(cache_path):
    assert not listdir(cache_path)


@when('the cache is initialized')
def initialize_cache(cache_path):
    FileSystemCache.init(directory=cache_path)
