import pytest
import conftest
from confgen.cli import ConfigTool

@pytest.fixture
def cfgtool(configtool_file):
    return ConfigTool(home=conftest.simplerepo('.'), config=configtool_file)


def test_load(cfgtool):
    loaded = cfgtool.load()
