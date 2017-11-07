import os
from os import mkdir
from os.path import exists

from behave import *
from behave.runner import Context

from storage.file_system import FileSystemCache

use_step_matcher("re")


@given("the storage directory does not exist")
def step_impl(context: Context):
    """
    Assume working directory is new, but halt if it's not empty.
    `environment.py` should have the before_scenario hook create it.
    """
    directory = context.scenario.temporary_directory_name
    assert not os.listdir(directory)


@when("the storage directory is initialized")
def step_impl(context: Context):
    """
    initialize within the temporary directory using the name 'test-spam-delete-me'
    """
    temporary_directory_name = context.scenario.temporary_directory_name
    directory = os.path.join(temporary_directory_name, 'test-spam-delete-me')
    FileSystemCache.init(directory)


@then("the storage directory exists")
def step_impl(context: Context):
    """
    check if 'test-spam-delete-me' directory exists
    """
    storage_directory_name = context.scenario.storage_directory_name
    assert exists(storage_directory_name)


@given("the storage directory exists")
def step_impl(context: Context):
    """
    create new temporary directory and create 'test-spam-delete-me' subdirectory
    """
    temporary_directory_name = context.scenario.temporary_directory_name
    directory = os.path.join(temporary_directory_name, 'test-spam-delete-me')
    mkdir(directory)


@then("the storage directory exits")
def step_impl(context: Context):
    temporary_directory_name = context.scenario.temporary_directory_name
    directory = os.path.join(temporary_directory_name, 'test-spam-delete-me')
    assert exists(directory)


@then("no exception is raised")
def step_impl(context: Context):
    """
    do nothing
    """
    ...


@when("the storage directory is ordered to self-destruct")
def step_impl(context: Context):
    """
    call destruct()
    """
    FileSystemCache.destruct(context.scenario.storage_directory_name)


@then("the storage directory does not exist")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    assert not exists(context.scenario.storage_directory_name)
