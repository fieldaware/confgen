from os.path import join
import pytest
import yaml

def assert_collected_inventory(tree):
    assert tree.inventory['mysql'] == 1.0
    assert tree.inventory['secret'] == 'password'
    assert tree['prod']['main'].inventory['mysql'] == 3.0
    assert tree['dev']['qa1'].inventory['mysql'] == 4.0
    assert tree['dev']['qa2'].inventory['mysql'] == 9.0
    assert tree['dev']['qa2'].inventory['new_key'] == 'my_value'
    assert tree['prod'].inventory['mysql'] == 2.0

def test_collected_inventory(inventory):
    assert_collected_inventory(inventory._tree)

def test_flatten_data_tree(inventory, confgen):
    t = inventory._tree
    assert t.as_dict['mysql'] == 1.0
    #assert t['mysql__source'] == '/'
    assert t.as_dict['secret'] == 'password'
    #assert t['secret__source'] == '/'
    assert t['dev']['qa1'].as_dict['mysql'] == 4.0
    #assert t['dev']['qa1']['mysql__source'] == '/ override: /dev/qa1'
    assert t['dev']['qa1'].as_dict['secret'] == 'password'
    #assert t['dev']['qa1']['secret__source'] == '/'
    assert t['dev']['qa2'].as_dict['mysql'] == 9.0
    #assert t['dev']['qa2']['mysql__source'] == '/ override: /dev/qa2'
    assert t['dev']['qa2'].as_dict['secret'] == 'password'
    #assert t['dev']['qa2']['secret__source'] == '/'
    assert t['dev']['qa2'].as_dict['new_key'] == 'my_value'
    #assert t['dev']['qa2']['new_key__source'] == '/dev/qa2'
    assert t['prod'].as_dict['mysql'] == 2.0
    #assert t['prod']['mysql__source'] == '/ override: /prod'
    assert t['prod'].as_dict['secret'] == 'password'
    #assert t['prod']['secret__source'] == '/'
    assert t['prod']['main'].as_dict['mysql'] == 3.0
    #assert t['prod']['main']['mysql__source'] == '/ override: /prod, /prod/main'
    assert t['prod']['main'].as_dict['secret'] == 'password'
    #assert t['prod']['main']['secret__source'] == '/'


@pytest.mark.parametrize('pattern,expected', (
    (
        'prod', {'infra/prod', 'infra/prod/main'}
    ),
    (
        '/.*', {'infra/dev/qa1', 'infra/dev/qa2', 'infra/prod', 'infra/prod/main'}
    ),
    (
        '.*', {
            'infra',
            'infra/dev/qa1',
            'infra/dev/qa2',
            'infra/prod',
            'infra/prod/main',
        }
    ),
    (
        '/dev/', {'infra/dev/qa1', 'infra/dev/qa2'}
    ),
))
def test_search_keys(inventory, pattern, expected):
    assert {i.path for i in inventory.search_key(pattern)} == expected


@pytest.mark.parametrize('pattern,expected', (
    ('my_value', {'infra/dev/qa2'}),
    ('1.0', {'infra', }),
    ('mysql', {'infra', 'infra/prod', 'infra/prod/main', 'infra/dev/qa1', 'infra/dev/qa2'}),
))
def test_search_values(inventory, pattern, expected):
    assert {i.path for i in inventory.search_value(pattern)} == expected

# opens file flushed to the inventory directory
open_inv = lambda i, p: yaml.load(open(join(i.inventory_dir, p, 'config.yaml')).read())

@pytest.mark.parametrize('path', (
    'infra',
    'infra/prod',
    'infra/prod/main',
    'infra/prod/main/webapp')
)
def test_set_new_value_existing_path(inventory, path):
    inventory.set(path, 'foo', 'bar')

    assert_collected_inventory(inventory._tree)
    assert inventory._tree.by_path(path).inventory['foo'] == "bar"
    assert open_inv(inventory, path.lstrip('infra/'))['foo'] == 'bar'

def test_set_set_value_new_path(inventory):
    with pytest.raises(KeyError):
        inventory.set('infra/prod/staging/demo1', 'foo', 'bar')

    assert_collected_inventory(inventory._tree)


def test_delete_existing_key(inventory):
    assert inventory._tree.by_path('infra').as_dict['secret'] == 'password'
    assert inventory.delete('infra', 'secret') == 'password'
    assert 'secret' not in inventory._tree.by_path('infra').as_dict
    assert open_inv(inventory, "") == {"mysql": 1.0}


def test_delete_last_remaining_key(inventory):
    assert inventory._tree.by_path('infra/dev/qa1').as_dict['mysql'] == 4.0
    assert inventory.delete('infra/dev/qa1', 'mysql') == 4.0
    assert {} == inventory._tree.by_path('infra/dev/qa1').inventory
    with pytest.raises(IOError):  # file should be gone
        open_inv(inventory, "dev/qa1")


def test_delete_non_existing_path(inventory):
    assert inventory.delete('infra/dev/qa3', 'mysql') is None
    with pytest.raises(KeyError):
        assert inventory._tree.by_path('infra/dev/qa3')
    assert_collected_inventory(inventory._tree)

def test_delete_non_existing_key(inventory):
    assert inventory.delete('infra/dev/qa2', 'psql') is None
    assert inventory._tree.by_path('infra/dev/qa2').inventory == {'mysql': 9.0, 'new_key': "my_value"}
    assert open_inv(inventory, 'dev/qa2') == {'mysql': 9.0, 'new_key': "my_value"}
    assert_collected_inventory(inventory._tree)


def test_flush(inventory):
    inventory._flush()
    assert open_inv(inventory, "") == {'mysql': 1.0, 'secret': "password"}
    assert open_inv(inventory, "prod") == {'mysql': 2.0}
    assert open_inv(inventory, "prod/main") == {'mysql': 3.0}
    assert open_inv(inventory, "dev/qa1") == {'mysql': 4.0}
    assert open_inv(inventory, "dev/qa2") == {'mysql': 9.0, 'new_key': 'my_value'}
