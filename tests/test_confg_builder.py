import pytest
import conftest
from confgen.cli import ConfigTool

@pytest.fixture
def cfgtool(configtool_file):
    return ConfigTool(home=conftest.simplerepo('.'), config=configtool_file)


def test_load_inventory(cfgtool):
    loaded = cfgtool.inventory()
    assert loaded == {
        '__kvs__': {'mysql': 1.0, 'secret': 'password'},
        'dev': {
            'qa1': {'__kvs__': {'mysql': 4.0}}
        },
        'prod': {
            '__kvs__': {'mysql': 2.0},
            'main': {'__kvs__': {'mysql': 3.0}}
        },
        'test': {'__kvs__': {'secret': 'plaintext'}}
    }

def test_load_inventory_default_inventory(cfgtool):
    loaded = cfgtool.inventory()
    assert loaded['dev']['inventory'] == {}  # default inventory is empty dict


def test_build_inventory(cfgtool):
    build = cfgtool.build()

    assert build == {
        '__kvs__': {'mysql': 1.0, 'secret': 'password'},
        'dev': {
            '__kvs__': {'mysql': 1.0, 'secret': 'password'},
            'qa1': {'__kvs__': {'mysql': 4.0, 'secret': 'password'}}},
        'prod': {
            '__kvs__': {'mysql': 2.0, 'secret': 'password'},
            'main': {'__kvs__': {'mysql': 3.0, 'secret': 'password'}}},
        'test': {'__kvs__': {'mysql': 1.0, 'secret': 'plaintext'}}
    }
