import pytest
import conftest
from confgen.cli import ConfigTool

@pytest.fixture
def cfgtool(configtool_file):
    return ConfigTool(home=conftest.simplerepo('.'), config=configtool_file)


def test_load_inventory(cfgtool):
    loaded = cfgtool.inventory()
    assert loaded == {
        'inventory': {
            'inventory': {'mysql': 1.0},
            'dev': {
                'qa1': {'inventory': {'mysql': 4.0}}
            },
            'prod': {
                'inventory': {'mysql': 2.0},
                'main': {'inventory': {'mysql': 3.0}}
            },
            'test': {}
        }
    }

def test_load_inventory_default_inventory(cfgtool):
    loaded = cfgtool.inventory()
    assert loaded['dev']['inventory'] == {}  # default inventory is empty dict
