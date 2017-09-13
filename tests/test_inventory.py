import pytest
import copy

def assert_collected_inventory(tree):
    assert tree.get('/').mysql == 1.0
    assert tree.get('/').secret == 'password'
    assert tree.get('/prod/main').mysql == 3.0
    assert tree.get('/dev/qa1').mysql == 4.0
    assert tree.get('/dev/qa2').mysql == 9.0
    assert tree.get('/dev/qa2').new_key == 'my_value'
    assert tree.get('/prod').mysql == 2.0
    assert tree.get('/test').secret == 'plaintext'

def test_load_inventory(inventory):
    assert_collected_inventory(inventory.collect())

def test_flatten_inventory(inventory):
    i = inventory.collect()

    assert i.flatten('/').mysql == 1.0
    assert i.flatten('/').mysql__source == '/'
    assert i.flatten('/').secret == 'password'
    assert i.flatten('/').secret__source == '/'
    assert i.flatten('/dev/qa1').mysql == 4.0
    assert i.flatten('/dev/qa1').mysql__source == '/ override: /dev/qa1'
    assert i.flatten('/dev/qa1').secret == 'password'
    assert i.flatten('/dev/qa1').secret__source == '/'
    assert i.flatten('/dev/qa2').mysql == 9.0
    assert i.flatten('/dev/qa2').mysql__source == '/ override: /dev/qa2'
    assert i.flatten('/dev/qa2').secret == 'password'
    assert i.flatten('/dev/qa2').secret__source == '/'
    assert i.flatten('/dev/qa2').new_key == 'my_value'
    assert i.flatten('/dev/qa2').new_key__source == '/dev/qa2'
    assert i.flatten('/prod').mysql == 2.0
    assert i.flatten('/prod').mysql__source == '/ override: /prod'
    assert i.flatten('/prod').secret == 'password'
    assert i.flatten('/prod').secret__source == '/'
    assert i.flatten('/prod/main').mysql == 3.0
    assert i.flatten('/prod/main').mysql__source == '/ override: /prod, /prod/main'
    assert i.flatten('/prod/main').secret == 'password'
    assert i.flatten('/prod/main').secret__source == '/'
    assert i.flatten('/test').mysql == 1.0
    assert i.flatten('/test').mysql__source == '/'
    assert i.flatten('/test').secret == 'plaintext'
    assert i.flatten('/test').secret__source == '/ override: /test'


@pytest.mark.parametrize('pattern,expected', (
    (
        'prod',
        {
            '/prod': {'mysql': 2.0},
            '/prod/main': {'mysql': 3.0}
        }
    ),
    (
        '/.*',
        {
            '/': {'mysql': 1.0, 'secret': 'password'},
            '/dev/qa1': {'mysql': 4.0},
            '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
            '/prod': {'mysql': 2.0},
            '/prod/main': {'mysql': 3.0},
            '/test': {'secret': 'plaintext'}
        }
    ),
    (
        '/dev/',
        {
            '/dev/qa1': {'mysql': 4.0},
            '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
        }
    ),
))
def test_search_keys(inventory, pattern, expected):
    assert inventory.search_key(pattern) == expected


@pytest.mark.parametrize('pattern,expected', (
    (
        'my_value',
        {'/dev/qa2': {'new_key': 'my_value'}, }
    ),
    (
        'plaintext',
        {'/test': {'secret': 'plaintext'}}
    ),
    (
        '1.0',
        {'/': {'mysql': 1.0, }}
    ),
))
def test_search_values(inventory, pattern, expected):
    assert inventory.search_value(pattern) == expected


def test_set_new_value_existing_path(inventory):
    inventory.set('/', 'foo', 'bar')
    loaded = inventory.collect()

    expected = copy.deepcopy(collected_inventory)
    expected['/']['foo'] = 'bar'
    assert loaded == expected

def test_set_set_value_new_path(inventory):
    inventory.set('/staging/demo1', 'foo', 'bar')
    loaded = inventory.collect()

    expected = copy.deepcopy(collected_inventory)
    expected['/staging/demo1'] = {'foo': 'bar'}
    assert loaded == expected

def test_delete_existing_key(inventory):
    inventory.delete('/', 'secret')

    loaded = inventory.collect()
    expected = copy.deepcopy(collected_inventory)
    expected['/'].pop('secret')
    assert loaded == expected

def test_delete_last_remaining_key(inventory):
    inventory.delete('/dev/qa1', 'mysql')

    loaded = inventory.collect()
    expected = copy.deepcopy(collected_inventory)
    expected['/dev/qa1'] = {}
    assert loaded == expected

def test_delete_non_existing_path(inventory):
    inventory.delete('/dev/qa3', 'mysql')

    loaded = inventory.collect()
    assert loaded == collected_inventory


def test_delete_non_existing_key(inventory):
    inventory.delete('/dev/qa2', 'psql')

    loaded = inventory.collect()
    assert loaded == collected_inventory
