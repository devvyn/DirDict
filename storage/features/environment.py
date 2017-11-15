from logging import info
from os import path
from shutil import rmtree
from tempfile import mkdtemp

from behave import model, runner

from storage.file_system import FileSystemStorage


def before_scenario(context: runner.Context, scenario: model.Step):
    dtemp = mkdtemp()
    scenario.temporary_directory_path = dtemp
    scenario.storage_path = path.join(dtemp, 'test-spam-delete-me')
    if context.feature.name == 'Save and load':
        FileSystemStorage.init(scenario.storage_path)
    info('Temporary directory created for "%s": %s', scenario.name, scenario.temporary_directory_path)


# noinspection PyUnresolvedReferences
def after_scenario(_, scenario: model.Scenario):
    rmtree(scenario.temporary_directory_path)
    info('Temporary directory deleted for "%s": %s', scenario.name, scenario.temporary_directory_path)
