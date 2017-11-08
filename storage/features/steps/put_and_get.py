from os import utime, stat, path, listdir

from behave import *

HOUR_IN_SECONDS = 60 * 60

use_step_matcher("re")


@given("I never want a file that's more than an hour old")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.time_to_live_hours = 1


@given("^a stored file that's 1 minute old$")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    storage_directory_name = context.scenario.storage_directory_name
    file_path = path.join(storage_directory_name, 'fresh-spam.txt')
    with open(file_path, mode='w') as fresh_file:
        fresh_file.write('fresh spam and eggs')
    file_stat = stat(file_path)
    atime, mtime = float(file_stat.st_atime_ns), float(file_stat.st_mtime_ns)
    utime(file_path, times=(atime, mtime - HOUR_IN_SECONDS))


@when("I request that key")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')


@then("I get the contents of the file that matches the key by name")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')


@given("^a key that's 61 minutes old$")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')


@then("the file is not loaded")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')


@step("that file no longer exists")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')


@given("no files in the storage directory")
def step_impl(context):
    """
    assume the storage directory is empty, but halt if not
    """
    storage_directory_name = context.scenario.storage_directory_name
    if listdir(storage_directory_name):
        raise FileExistsError(f'Directory {storage_directory_name} contains files when it should not')


@when("I request any file")
def step_impl(context):
    """
    make up a file name and attempt to look it up in vain
    """
    raise NotImplementedError(f'{__name__} not implemented')


@then("a KeyError exception is raised")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')


@step("the storage directory is still empty")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise NotImplementedError(f'{__name__} not implemented')
