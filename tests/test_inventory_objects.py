import pytest
from confgen.inventory import Node, DB

def test_str():
    node = Node("foo_node")
    assert str(node) == "foo_node"

def test_missing_attr():
    node = Node("foo_node")
    with pytest.raises(AttributeError):
        node.foo

def test_no_attrs_iter():
    node = Node("foo_node")
    assert [i for i in node] == []

def test_getttr_empty():
    node = Node("foo_node")
    with pytest.raises(KeyError):
        node['foo']

def test_attr_str():
    node = Node("foo", data={'foo': 'bar'})
    assert node.foo == 'bar'

def test_attr_multiple_dict():
    node = Node("foo", data={'foo': 'bar', 'list': [1, 2, 3], 'int': 5})
    assert node.int == 5
    assert node.foo == 'bar'
    assert node.list == [1, 2, 3]

def test_2_level_node():
    db = Node("root", data={'level1': 'root'}, children=[
        Node("leaf1", data={'level2': 'foo1'}),
        Node("leaf2", data={'level2': 'foo2'})
    ])

    assert db.level1 == 'root'
    assert db['leaf1'].level2 == 'foo1'
    assert db['leaf2'].level2 == 'foo2'

    leafs = [getattr(i, 'level2') for i in db]
    # assert you cannot rely on the order in the list
    assert set(leafs) == {'foo1', 'foo2'}

def test_db_iterate_over_root():
    db = DB()
    nodes = [i for i in db.nodes('/')]
    assert len(nodes) == 1
    assert str(nodes[0]) == '/'

@pytest.mark.parametrize("paths", (
    [],
    ['/prod', '/prod/main'],
    ['/prod', '/prod/main', '/dev', '/dev/qa1'],
    ['/prod', '/dev', '/staging'],
))
def test_db_all_nodes(paths):
    db = DB()
    for path in paths:
        db.set(path, {})

    assert set([i.full_path for i in db.all_nodes()]) == set(['/'] + paths)

def test_db_update_root():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    assert db.get("/").attr_foo == "bar"
    assert db.get("/").full_path == "/"

def test_db_add_to_root():
    db = DB()
    db.set('/prod', attrs={'attr_foo': 'prod_attr'})
    assert db.get('/prod').attr_foo == "prod_attr"

def test_db_nested_paths():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/prod', attrs={'attr_foo': 'prod_attr'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert db.get('/').attr_foo == "bar"
    assert db.get('/prod').attr_foo == "prod_attr"
    assert db.get('/prod/main').attr_foo == "main_attr"

    assert db.get('/').full_path == "/"
    assert db.get('/prod').full_path == "/prod"
    assert db.get('/prod/main').full_path == "/prod/main"

def test_db_update_existing_node():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/', attrs={'attr_foo2': 'bar2'})
    db.set('/prod', attrs={'attr_foo': 'prod_attr'})
    db.set('/prod', attrs={'attr_foo2': 'prod_attr2'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    db.set('/prod/main', attrs={'attr_foo2': 'main_attr2'})
    assert db.get('/').attr_foo2 == "bar2"
    assert db.get('/prod').attr_foo2 == "prod_attr2"
    assert db.get('/prod/main').attr_foo2 == "main_attr2"

    assert db.get('/').full_path == "/"
    assert db.get('/prod').full_path == "/prod"
    assert db.get('/prod/main').full_path == "/prod/main"

def test_db_get_no_middle_path():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert db.get('/').attr_foo == "bar"
    assert db.get('/prod/main').attr_foo == "main_attr"

def test_db_flatten_no_middle_path():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert db.flatten('/').attr_foo == "bar"
    assert db.flatten('/prod').attr_foo == "bar"
    assert db.flatten('/prod/main').attr_foo == "main_attr"

def test_db_flatten_full():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar', 'default': 'default_root'})
    db.set('/prod', attrs={'other_attr': 'foo'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})

    assert db.flatten('/').attr_foo == "bar"
    assert db.flatten('/').default == "default_root"

    assert db.flatten('/prod').other_attr == "foo"
    assert db.flatten('/prod').attr_foo == "bar"
    assert db.flatten('/prod').default == "default_root"

    assert db.flatten('/prod/main').attr_foo == 'main_attr'
    assert db.flatten('/prod/main').other_attr == 'foo'
    assert db.flatten('/prod/main').default == 'default_root'

def test_falatten_with_sources():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/prod', attrs={'attr_foo': 'foo'})

    assert db.flatten('/prod').attr_foo == 'foo'
    assert db.flatten('/prod').attr_foo__source == "/ override: /prod"

    assert db.flatten('/').attr_foo == "bar"
    assert db.flatten('/').attr_foo__source == "/"
