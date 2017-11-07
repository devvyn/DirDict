from os import O_RDWR, utime, stat, path

from behave import *

HOUR_IN_SECONDS = 60 * 60


@given("I never want a file that's more than an hour old")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.time_to_live_hours = 1


@given("a stored file that's a minute old")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    storage_directory_name = context.scenario.storage_directory_name
    file_path = path.join(storage_directory_name, 'fresh-spam,txt')
    with open(file_path, mode=O_RDWR) as fresh_file:
        fresh_file.write('fresh spam and eggs')
        with stat(file_path) as file_stat:
            atime, mtime = float(file_stat['st_atime']), float(file_stat['st_mtime'])
        utime(file_path, times=(atime, mtime - HOUR_IN_SECONDS))


@when("I request that file")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@then("I receive the contents of that file")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@given("a stored file that's 66 minutes old")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@then("the file is not loaded")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@step("that file no longer exists")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@given("no files")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@when("I request any file")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@then("a KeyError exception is raised")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@step("the storage directory is still empty")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass
