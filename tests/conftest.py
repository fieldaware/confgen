import os
from click.testing import CliRunner
import pytest

pwd = os.path.dirname(os.path.abspath(__file__))

simplerepo = lambda x: os.path.join(os.path.join(pwd, 'simplerepo'), x)


@pytest.fixture
def configtool_file(request):
    return simplerepo('configtool.yaml')

@pytest.fixture
def runner(configtool_file):
    runner = CliRunner()
    return runner
