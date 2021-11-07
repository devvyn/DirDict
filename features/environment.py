from logging import info
from os import path
from shutil import rmtree
from tempfile import mkdtemp

from behave import model, runner
from behave.model import Scenario
from behave.runner import Context

from dirdict.functions import initialize_base_path



def before_scenario(context: runner.Context, scenario: model.Step):
    """" Always make a new directory for guaranteed state """
    temporary_directory = mkdtemp()
    scenario.temporary_workspace_for_testing = temporary_directory
    info('Temporary directory created for "%s": %s', scenario.name, scenario.temporary_workspace_for_testing)


# noinspection PyUnresolvedReferences
def after_scenario(_: Context, scenario: Scenario):
    rmtree(scenario.temporary_workspace_for_testing)
    info('Temporary directory deleted for "%s": %s', scenario.name, scenario.temporary_workspace_for_testing)
