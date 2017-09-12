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
    tree = Node("root", attributes={'level1': 'root'}, nodes=[
        Node("leaf1", attributes={'level2': 'foo1'}),
        Node("leaf2", attributes={'level2': 'foo2'})
    ])

    assert tree.level1 == 'root'
    assert tree['leaf1'].level2 == 'foo1'
    assert tree['leaf2'].level2 == 'foo2'

    leafs = [getattr(i, 'level2') for i in tree]
    # assert you cannot rely on the order in the list
    assert set(leafs) == {'foo1', 'foo2'}

def test_tree_update_root():
    tree = DB()
    tree.set('/', attrs={'attr_foo': 'bar'})
    assert tree.get("/").attr_foo == "bar"

def test_tree_add_to_root():
    tree = DB()
    tree.set('/prod', attrs={'attr_foo': 'prod_attr'})
    assert tree.get('/prod').attr_foo == "prod_attr"

def test_tree_nested_paths():
    tree = DB()
    tree.set('/', attrs={'attr_foo': 'bar'})
    tree.set('/prod', attrs={'attr_foo': 'prod_attr'})
    tree.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert tree.get('/').attr_foo == "bar"
    assert tree.get('/prod').attr_foo == "prod_attr"
    assert tree.get('/prod/main').attr_foo == "main_attr"

def test_tree_update_existing_nodes():
    tree = DB()
    tree.set('/', attrs={'attr_foo': 'bar'})
    tree.set('/', attrs={'attr_foo2': 'bar2'})
    tree.set('/prod', attrs={'attr_foo': 'prod_attr'})
    tree.set('/prod', attrs={'attr_foo2': 'prod_attr2'})
    tree.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    tree.set('/prod/main', attrs={'attr_foo2': 'main_attr2'})
    assert tree.get('/').attr_foo2 == "bar2"
    assert tree.get('/prod').attr_foo2 == "prod_attr2"
    assert tree.get('/prod/main').attr_foo2 == "main_attr2"

def test_tree_get_no_middle_path():
    tree = DB()
    tree.set('/', attrs={'attr_foo': 'bar'})
    tree.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert tree.get('/').attr_foo == "bar"
    assert tree.get('/prod/main').attr_foo == "main_attr"

def test_tree_unfold_no_middle_path():
    tree = DB()
    tree.set('/', attrs={'attr_foo': 'bar'})
    tree.set('/prod/main', attrs={'attr_foo': 'main_attr'})
    assert tree.flatten('/').attr_foo == "bar"
    assert tree.flatten('/prod').attr_foo == "bar"
    assert tree.flatten('/prod/main').attr_foo == "main_attr"

def test_tree_unfold_full():
    tree = DB()
    tree.set('/', attrs={'attr_foo': 'bar', 'default': 'default_root'})
    tree.set('/prod', attrs={'other_attr': 'foo'})
    tree.set('/prod/main', attrs={'attr_foo': 'main_attr'})

    assert tree.flatten('/').attr_foo == "bar"
    assert tree.flatten('/').default == "default_root"

    assert tree.flatten('/prod').other_attr == "foo"
    assert tree.flatten('/prod').attr_foo == "bar"
    assert tree.flatten('/prod').default == "default_root"

    assert tree.flatten('/prod/main').attr_foo == 'main_attr'
    assert tree.flatten('/prod/main').other_attr == 'foo'
    assert tree.flatten('/prod/main').default == 'default_root'
