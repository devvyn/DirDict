from os import utime, stat, path, listdir

from behave import *
from behave import runner

HOUR_IN_SECONDS = 60 * 60

use_step_matcher("re")


@given("^I don't accept keys more than an hour old$")
def step_impl(context: runner.Context):
    """
    set key expiry time, in seconds
    """
    context.time_to_live_hours = 1


@given("^a stored file that's 1 minute old$")
def step_impl(context: runner.Context):
    """
    create file and set modified time to one minute ago
    """
    storage_directory_path = context.scenario.storage_directory_path
    file_path = path.join(storage_directory_path, 'fresh-spam.txt')
    with open(file_path, mode='w') as fresh_file:
        fresh_file.write('fresh spam and eggs')
    file_stat = stat(file_path)
    atime, mtime = float(file_stat.st_atime_ns), float(file_stat.st_mtime_ns)
    utime(file_path, times=(atime, mtime - HOUR_IN_SECONDS))


@given("^an empty storage directory$")
def step_impl(context):
    """
    assume the storage directory is empty, but halt if not
    """
    storage_directory_path = context.scenario.storage_directory_path
    if listdir(storage_directory_path):
        raise FileExistsError(f'Directory {storage_directory_path} contains files when it should not')


