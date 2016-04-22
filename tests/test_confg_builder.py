def test_load_inventory(inventory):
    loaded = inventory.collect()
    assert loaded == {
        '/': {'mysql': 1.0, 'secret': 'password'},
        '/dev/qa1': {'mysql': 4.0},
        '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
        '/prod': {'mysql': 2.0},
        '/prod/main': {'mysql': 3.0},
        '/test': {'secret': 'plaintext'},
    }


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
    assert loaded == {
        '/': {'mysql': 1.0, 'secret': 'password', 'foo': 'bar'},
        '/dev/qa1': {'mysql': 4.0},
        '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
        '/prod': {'mysql': 2.0},
        '/prod/main': {'mysql': 3.0},
        '/test': {'secret': 'plaintext'},
    }

def test_set_set_value_new_path(inventory):
    inventory.set('/staging/demo1', 'foo', 'bar')
    loaded = inventory.collect()
    assert loaded == {
        '/': {'mysql': 1.0, 'secret': 'password'},
        '/dev/qa1': {'mysql': 4.0},
        '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
        '/prod': {'mysql': 2.0},
        '/prod/main': {'mysql': 3.0},
        '/test': {'secret': 'plaintext'},
        '/staging/demo1': {'foo': 'bar'},
    }
