import pytest

def assert_collected_inventory(tree):
    assert tree.inventory['mysql'] == 1.0
    assert tree.inventory['secret'] == 'password'
    assert tree['prod']['main'].inventory['mysql'] == 3.0
    assert tree['dev']['qa1'].inventory['mysql'] == 4.0
    assert tree['dev']['qa2'].inventory['mysql'] == 9.0
    assert tree['dev']['qa2'].inventory['new_key'] == 'my_value'
    assert tree['prod'].inventory['mysql'] == 2.0

def test_collectg_inventory(inventory):
    inventory.collect()
    assert_collected_inventory(inventory._tree)

def test_flatten_data_tree(inventory, confgen):
    inventory.collect()
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


# @pytest.mark.parametrize('pattern,expected', (
#     (
#         'prod', {
#             '/prod': {'mysql': 2.0},
#             '/prod/main': {'mysql': 3.0}
#         }
#     ),
#     (
#         '/.*', {
#             '/': {'mysql': 1.0, 'secret': 'password'},
#             '/dev/qa1': {'mysql': 4.0},
#             '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
#             '/prod': {'mysql': 2.0},
#             '/prod/main': {'mysql': 3.0},
#             '/test': {'secret': 'plaintext'}
#         }
#     ),
#     (
#         '/dev/', {
#             '/dev/qa1': {'mysql': 4.0},
#             '/dev/qa2': {'mysql': 9.0, 'new_key': 'my_value'},
#         }
#     ),
# ))
# def test_search_keys(inventory, pattern, expected):
#     assert inventory.search_key(pattern) == expected
#
#
# @pytest.mark.parametrize('pattern,expected', (
#     ('my_value', {'/dev/qa2': {'new_key': 'my_value'}}),
#     ('plaintext', {'/test': {'secret': 'plaintext'}}),
#     ('1.0', {'/': {'mysql': 1.0, }}),
# ))
# def test_search_values(inventory, pattern, expected):
#     assert inventory.search_value(pattern) == expected
#
#
# def test_set_new_value_existing_path(inventory):
#     inventory.set('/', 'foo', 'bar')
#     loaded = inventory.collect()
#
#     assert_collected_inventory(loaded)
#     assert loaded.get('/').foo == "bar"
#
# def test_set_set_value_new_path(inventory):
#     inventory.set('/staging/demo1', 'foo', 'bar')
#     loaded = inventory.collect()
#
#     assert_collected_inventory(loaded)
#     assert loaded.get('/staging/demo1').foo == "bar"
#
#
# def test_delete_existing_key(inventory):
#     inventory.delete('/', 'secret')
#
#     tree = inventory.collect()
#     assert tree.get('/').mysql == 1.0
#     assert tree.get('/prod/main').mysql == 3.0
#     assert tree.get('/dev/qa1').mysql == 4.0
#     assert tree.get('/dev/qa2').mysql == 9.0
#     assert tree.get('/dev/qa2').new_key == 'my_value'
#     assert tree.get('/prod').mysql == 2.0
#     assert tree.get('/test').secret == 'plaintext'
#
#
# def test_delete_last_remaining_key(inventory):
#     inventory.delete('/dev/qa1', 'mysql')
#
#     tree = inventory.collect()
#     assert tree.get('/').mysql == 1.0
#     assert tree.get('/prod/main').mysql == 3.0
#     assert tree.get('/dev/qa2').mysql == 9.0
#     assert tree.get('/dev/qa2').new_key == 'my_value'
#     assert tree.get('/prod').mysql == 2.0
#     assert tree.get('/test').secret == 'plaintext'
#
#
# def test_delete_non_existing_path(inventory):
#     inventory.delete('/dev/qa3', 'mysql')
#
#     loaded = inventory.collect()
#     assert_collected_inventory(loaded)
#
# def test_delete_non_existing_key(inventory):
#     inventory.delete('/dev/qa2', 'psql')
#
#     loaded = inventory.collect()
#     assert_collected_inventory(loaded)
