def test_load_inventory(inventory):
    loaded = inventory.collect()
    assert loaded == {
        '/': {'mysql': 1.0, 'secret': 'password'},
        '/dev/qa1': {'mysql': 4.0},
        '/dev/qa2': {'mysql': 9.0},
        '/prod': {'mysql': 2.0},
        '/prod/main': {'mysql': 3.0},
        '/test': {'secret': 'plaintext'},
    }

def test_build_inventory(inventory):
    public_inventory = inventory.build()

    assert public_inventory == {
        '/': {'mysql': 1.0, 'secret': 'password'},
        '/dev/qa1': {'mysql': 4.0, 'secret': 'password'},
        '/dev/qa2': {'mysql': 9.0, 'secret': 'password'},
        '/prod': {'mysql': 2.0, 'secret': 'password'},
        '/prod/main': {'mysql': 3.0, 'secret': 'password'},
        '/test': {'mysql': 1.0, 'secret': 'plaintext'}
    }