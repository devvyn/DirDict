from logging import info
from os import path
from shutil import rmtree
from tempfile import mkdtemp

from storage.file_system import FileSystemCache


def before_feature(_, feature):
    if 'directory_setup' != feature.name:
        FileSystemCache.init('test-spam-delete-me')


def before_scenario(_, scenario):
    dtemp = mkdtemp()
    scenario.temporary_directory_name = dtemp
    scenario.storage_directory_name = path.join(dtemp, 'test-spam-delete-me')
    info('Temporary directory created at %s for %s', scenario.temporary_directory_name, scenario.name)


def after_scenario(_, scenario):
    rmtree(scenario.temporary_directory_name)
