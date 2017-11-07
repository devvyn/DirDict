from logging import info
from os import path
from shutil import rmtree
from tempfile import mkdtemp

from behave import model, runner

from storage.file_system import FileSystemCache


def before_scenario(context: runner.Context, scenario: model.Step):
    dtemp = mkdtemp()
    scenario.temporary_directory_name = dtemp
    scenario.storage_directory_name = path.join(dtemp, 'test-spam-delete-me')
    if context.feature.name == 'Save and load':
        FileSystemCache.init(scenario.storage_directory_name)
    info('Temporary directory created for "%s": %s', scenario.name, scenario.temporary_directory_name)


# noinspection PyUnresolvedReferences
def after_scenario(_, scenario: model.Scenario):
    rmtree(scenario.temporary_directory_name)
    info('Temporary directory deleted for "%s": %s', scenario.name, scenario.temporary_directory_name)
