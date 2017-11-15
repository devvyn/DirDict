import os
from os import mkdir
from os.path import exists

from behave import *
from behave.runner import Context

from storage.file_system import FileSystemStorage


@given("the storage directory does not exist")
def step_impl(context: Context):
    """
    Assume working directory is new, but halt if it's not empty.
    `environment.py` should have the before_scenario hook create it.
    """
    directory = context.scenario.temporary_directory_path
    assert not os.listdir(directory)


@when("the storage directory is initialized")
def step_impl(context: Context):
    """
    initialize within the temporary directory using the name 'test-spam-delete-me'
    """
    temporary_directory_path = context.scenario.temporary_directory_path
    directory = os.path.join(temporary_directory_path, 'test-spam-delete-me')
    FileSystemStorage.init(directory)


@then("the storage directory exists")
def step_impl(context: Context):
    """
    check if 'test-spam-delete-me' directory exists
    """
    storage_path = context.scenario.storage_path
    assert exists(storage_path)


@given("the storage directory exists")
def step_impl(context: Context):
    """
    create new temporary directory and create 'test-spam-delete-me' subdirectory
    """
    temporary_directory_path = context.scenario.temporary_directory_path
    directory = os.path.join(temporary_directory_path, 'test-spam-delete-me')
    mkdir(directory)


@then("the storage directory exits")
def step_impl(context: Context):
    temporary_directory_path = context.scenario.temporary_directory_path
    directory = os.path.join(temporary_directory_path, 'test-spam-delete-me')
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
    FileSystemStorage.destruct(context.scenario.storage_path)


@then("the storage directory does not exist")
def step_impl(context):
    """
    check directory doesn't exist
    """
    assert not exists(context.scenario.storage_path)
