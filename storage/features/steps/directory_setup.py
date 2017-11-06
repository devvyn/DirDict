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
    create new temporary directory and halt if not empty
    """
    directory = context.scenario.temporary_directory_name
    assert not os.listdir(directory)


@when("the storage directory is initialized")
def step_impl(context: Context):
    """
    initialize within the temporary directory using the name 'test-spam-delete-me'
    """
    directory = os.path.join(context.scenario.temporary_directory_name, 'test-spam-delete-me')
    FileSystemCache.init(directory)


@then("the storage directory exists")
def step_impl(context: Context):
    """
    check if 'test-spam-delete-me' directory exists
    """
    assert exists(context.scenario.storage_directory_name)


@given("the storage directory exists")
def step_impl(context: Context):
    """
    create new temporary directory and create 'test-spam-delete-me' subdirectory
    """
    directory = os.path.join(context.scenario.temporary_directory_name, 'test-spam-delete-me')
    mkdir(directory)


@then("the storage directory exits")
def step_impl(context: Context):
    directory = os.path.join(context.scenario.temporary_directory_name, 'test-spam-delete-me')
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
