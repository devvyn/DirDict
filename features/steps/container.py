from pathlib import Path

from behave import *
from behave import runner
from behave.runner import Context

from dirdict.functions import initialize_base_path, remove_base_path


@given('the storage directory shall be named "{directory_name}"')
def step_impl(context: runner.Context, directory_name: str):
    context.storage_directory_name = directory_name

@then("the storage directory does not exist")
def step_impl(context: Context):
    path = Path(context.scenario.temporary_workspace_for_testing, context.storage_directory_name)
    assert not path.exists()


@when("the storage directory is initialized")
def step_impl(context: Context):
    directory = Path(context.scenario.temporary_workspace_for_testing, context.storage_directory_name)
    initialize_base_path(directory)


@then("the storage directory exists")
def step_impl(context: Context):
    storage_path = Path(context.scenario.temporary_workspace_for_testing, context.storage_directory_name)
    assert Path(storage_path).exists()



@when("the storage directory is ordered to self-destruct")
def step_impl(context: Context):
    remove_base_path(context.scenario.storage_path)


@given("the storage directory already exists")
def step_impl(context: runner.Context):
    context.execute_steps("When the storage directory is initialized")
