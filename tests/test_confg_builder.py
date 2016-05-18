import copy
collected_inventory = {
    '/': {'mysql': 1.0, 'secret': 'password'},
    '/prod/main': {'mysql': 3.0},
    '/dev/qa1': {'mysql': 4.0},
    '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
    '/prod': {'mysql': 2.0},
    '/test': {'secret': 'plaintext'},
}

def test_load_inventory(inventory):
    loaded = inventory.collect()
    assert loaded == collected_inventory

def test_build_inventory(inventory):
    public_inventory = inventory.build()

    assert public_inventory == {
        '/': {
            'mysql': 1.0,
            'mysql__source': 'mysql:/',
            'secret': 'password',
            'secret__source': 'secret:/',
        },
        '/dev/qa1': {
            'mysql': 4.0,
            'mysql__source': 'mysql:/ override:/dev/qa1',
            'secret': 'password',
            'secret__source': 'secret:/',
        },
        '/dev/qa2': {
            'mysql': 9.0,
            'mysql__source': 'mysql:/ override:/dev/qa2',
            'secret': 'password',
            'secret__source': 'secret:/',
            'new_key': 'my_value',
            'new_key__source': 'new_key:/dev/qa2',
        },
        '/prod': {
            'mysql': 2.0,
            'mysql__source': 'mysql:/ override:/prod',
            'secret': 'password',
            'secret__source': 'secret:/',
        },
        '/prod/main': {
            'mysql': 3.0,
            'mysql__source': 'mysql:/ override:/prod,/prod/main',
            'secret': 'password',
            'secret__source': 'secret:/',
        },
        '/test': {
            'mysql': 1.0,
            'mysql__source': 'mysql:/',
            'secret': 'plaintext',
            'secret__source': 'secret:/ override:/test',
        }
    }

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
