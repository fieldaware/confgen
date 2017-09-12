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
    node = Node(attributes={'foo': 'bar'})
    assert node.foo == 'bar'

def test_attr_multiple_dict():
    node = Node(attributes={'foo': 'bar', 'list': [1, 2, 3], 'int': 5})
    assert node.int == 5
    assert node.foo == 'bar'
    assert node.list == [1, 2, 3]

def test_2_level_node():
    db = Node("root", attributes={'level1': 'root'}, nodes=[
        Node("leaf1", attributes={'level2': 'foo1'}),
        Node("leaf2", attributes={'level2': 'foo2'})
    ])

    assert db.level1 == 'root'
    assert db['leaf1'].level2 == 'foo1'
    assert db['leaf2'].level2 == 'foo2'

    leafs = [getattr(i, 'level2') for i in db]
    # assert you cannot rely on the order in the list
    assert set(leafs) == {'foo1', 'foo2'}

def test_db_update_root():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    assert db.get("/").attr_foo == "bar"

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

def test_db_get_no_middle_path():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert db.get('/').attr_foo == "bar"
    assert db.get('/prod/main').attr_foo == "main_attr"

def test_db_unfold_no_middle_path():
    db = DB()
    db.set('/', attrs={'attr_foo': 'bar'})
    db.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert db.flatten('/').attr_foo == "bar"
    assert db.flatten('/prod').attr_foo == "bar"
    assert db.flatten('/prod/main').attr_foo == "main_attr"

def test_db_unfold_full():
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