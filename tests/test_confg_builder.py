import pytest
import conftest
from confgen.cli import Inventory

@pytest.fixture
def inventory():
    return Inventory(home=conftest.simplerepo('.'))


def test_load_inventory(inventory):
    loaded = inventory.collect()
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

def test_load_inventory_default_inventory(inventory):
    loaded = inventory.collect()
    assert loaded['dev']['inventory'] == {}  # default inventory is empty dict


def test_build_inventory(inventory):
    build = inventory.build()

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
