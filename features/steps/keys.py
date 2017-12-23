from os import utime, listdir
from pathlib import Path

from behave import *
from behave import runner

from dirdict.functions import get, keys, set_, del_, initialize_base_path

SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60

@given("I don't accept keys more than 60 minutes old")
def step_impl(context: runner.Context):
    context.time_to_live_seconds = 1 * MINUTES_PER_HOUR * SECONDS_PER_MINUTE


@given("^a file$")
@given("^a file that's 1 minute old$")
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    file_path = Path(storage_path, context.example_file_name)
    with open(file_path, mode='w') as fresh_file:
        fresh_file.write(context.example_text)
    file_stat = file_path.stat()
    atime, mtime = float(file_stat.st_atime_ns), float(file_stat.st_mtime_ns)
    file_path.utime( times=(atime, mtime - SECONDS_PER_MINUTE))


@given("an empty storage directory")
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    if listdir(storage_path):
        raise FileExistsError(f'Directory {storage_path} contains files when it should not')


@when('I save some text to a key named "{key_name}"')
def step_impl(context: runner.Context, key_name):
    some_text = context.example_text
    key = Path(context.scenario.storage_path, key_name)  # @todo: use key_name without path
    set_(key, some_text.encode('utf-8'))  # @todo: use class


@then('the storage directory contains a file named "{file_name}"')
def step_impl(context: runner.Context, file_name: (str, bytes)):
    storage_path = context.scenario.storage_path
    file_path = Path(storage_path, file_name)
    assert file_path.exists()


@then("that file contains the specified text")
def step_impl(context):
    specified_text = context.example_text
    storage_path = context.scenario.storage_path
    file_name = context.example_file_name
    file_path = Path(storage_path, file_name)
    with open(file_path) as file_for_key:
        assert file_for_key.read() == specified_text


@when("I request that key")
@when("I request any specific key by name")
def step_impl(context: runner.Context):
    try:
        context.results = get(context.scenario.storage_path, context.example_file_name,
                              ttl_seconds=context.time_to_live_seconds)
    except KeyError as e:
        context.exception = e
    else:
        del context.exception


@then("^a 'KeyError' exception is raised$")
def step_impl(context: runner.Context):
    assert 'exception' in context
    assert KeyError is type(context.exception)  # @todo: check this line, I made it up


@then("I get the contents of the file that matches the key by name")
def step_impl(context: runner.Context):
    expected_text = 'Spam & eggs with toast and Spam'
    assert context.results == expected_text


@given("^a file that's 61 minutes old$")
def step_impl(context: runner.Context):
    storage_path = context.scenario.storage_path
    interval = 61
    file_path = Path(storage_path, context.example_file_name)
    with open(file_path, mode='w') as fresh_file:
        fresh_file.write(context.example_text)
    file_stat = file_path.stat()
    atime, mtime = float(file_stat.st_atime_ns), float(file_stat.st_mtime_ns)
    file_path.utime(times=(atime, mtime - interval))


@when("I delete the storage key that matches the file's name")
def step_impl(context: runner.Context):
    del_(context.example_file_name)


@then("that storage key is not in the collection of stored keys")
def step_impl(context: runner.Context):
    assert context.example_file_name not in keys(context.scenario.storage_path)


@then("the storage directory contains no file that matches the key by name")
def step_impl(context: runner.Context):
    assert context.example_file_name not in listdir(context.scenario.storage_path)


@given("the storage directory contains a file with a given name")
def step_impl(context: runner.Context):
    assert get(context.example_file_name)


@step('my example file name is "{file_name}"')
def step_impl(context: runner.Context, file_name: str):
    context.example_file_name = file_name


@step('my example text is "{example_text}"')
def step_impl(context: runner.Context, example_text: str):
    context.example_text = example_text


@step('my example key name is "{key_name}"')
def step_impl(context: runner.Context, key_name: str):
    context.example_key_name = key_name


@step("the container is initialized")
def step_impl(context):
    initialize_base_path(context.scenario.storage_path)
