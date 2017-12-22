from os import utime, stat, listdir
from pathlib import Path

from behave import *
from behave import runner

from dirdict import DirDict
from dirdict.functions import get, keys, set_

TEST_FILE_NAME2 = "whatever"

TEST_FILE_NAME1 = 'fresh-spam.txt'

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60


@given("I don't accept keys more than 60 minutes old")
def step_impl(context: runner.Context):
    context.time_to_live_seconds = 1 * MINUTES_PER_HOUR * SECONDS_PER_MINUTE


@given("^a file that's 1 minute old$")
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    file_path = Path(storage_path, TEST_FILE_NAME1)
    with open(file_path, mode='w') as fresh_file:
        fresh_file.write('fresh spam and eggs')
    file_stat = stat(bytearray(file_path))
    atime, mtime = float(file_stat.st_atime_ns), float(file_stat.st_mtime_ns)
    utime(bytearray(file_path), times=(atime, mtime - SECONDS_PER_MINUTE))


@given("an empty storage directory")
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    if listdir(storage_path):
        raise FileExistsError(f'Directory {storage_path} contains files when it should not')


@when('I save some text to a key named "whatever"')
def step_impl(context: runner.Context):
    some_text = 'Spam & eggs with toast and Spam'
    key = TEST_FILE_NAME2
    set_(key, some_text.encode('utf-8'))


@then('the storage directory contains a file named "whatever"')
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    file_path = Path(storage_path, TEST_FILE_NAME2)
    assert file_path.exists()


@then("that file contains the specified text")
def step_impl(context):
    storage_path = context.scenario.storage_path
    specified_text = 'Spam & eggs with toast and Spam'
    file_path = Path(storage_path, TEST_FILE_NAME1)
    with open(file_path) as file_for_key:
        assert file_for_key.read() == specified_text


@when("I request that key")
@when("I request any specific key by name")
def step_impl(context: runner.Context):
    try:
        context.results = get(context.scenario.storage_path, TEST_FILE_NAME1, ttl_seconds=context.time_to_live_seconds)
    except KeyError as e:
        context.exception = e
    else:
        del context.exception


@then("the absence of the specified key is signalled")
def step_impl(context: runner.Context):
    assert 'exception' in context


@then("I get the contents of the file that matches the key by name")
def step_impl(context: runner.Context):
    expected_text = 'Spam & eggs with toast and Spam'
    assert context.results == expected_text


@given("^a file that's 61 minutes old$")
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    interval = 61
    file_path = Path(storage_path, TEST_FILE_NAME1)
    with open(file_path, mode='w') as fresh_file:
        fresh_file.write('fresh spam and eggs')
    file_stat = stat(file_path)
    atime, mtime = float(file_stat.st_atime_ns), float(file_stat.st_mtime_ns)
    utime(file_path, times=(atime, mtime - interval))


@when("I delete the storage key that matches the file's name")
def step_impl(context: runner.Context):
    DirDict.del_(TEST_FILE_NAME1)


@then("that storage key is not in the collection of stored keys")
def step_impl(context: runner.Context):
    assert TEST_FILE_NAME1 not in keys(context.scenario.storage_path)


@then("the storage directory contains no file that matches the key by name")
def step_impl(context: runner.Context):
    assert TEST_FILE_NAME1 not in listdir(context.scenario.storage_path)


@given("the storage directory contains a file with a given name")
def step_impl(context: runner.Context):
    assert get(TEST_FILE_NAME1)
