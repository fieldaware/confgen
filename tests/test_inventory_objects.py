import pytest
from confgen.inventory import Node, Tree

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
    tree = Tree()
    tree.set('/', attr={'attr_foo': 'bar'})
    assert tree.get("/").attr_foo == "bar"

def test_tree_add_to_root():
    tree = Tree()
    tree.set('/prod', attr={'attr_foo': 'prod_attr'})
    assert tree.get('/prod').attr_foo == "prod_attr"

def test_tree_nested_paths():
    tree = Tree()
    tree.set('/', attr={'attr_foo': 'bar'})
    tree.set('/prod', attr={'attr_foo': 'prod_attr'})
    tree.set('/prod/main', attr={'attr_foo': 'main_attr'})
    assert tree.get('/').attr_foo == "bar"
    assert tree.get('/prod').attr_foo == "prod_attr"
    assert tree.get('/prod/main').attr_foo == "main_attr"

def test_tree_get_no_middle_path():
    tree = Tree()
    tree.set('/', attr={'attr_foo': 'bar'})
    tree.set('/prod/main', attr={'attr_foo': 'main_attr'})
    assert tree.get('/').attr_foo == "bar"
    assert tree.get('/prod/main').attr_foo == "main_attr"

def test_tree_unfold_no_middle_path():
    tree = Tree()
    tree.set('/', attr={'attr_foo': 'bar'})
    tree.set('/prod/main', attr={'attr_foo': 'main_attr'})
    assert tree.unfold('/').attr_foo == "bar"
    assert tree.unfold('/prod').attr_foo == "bar"
    assert tree.unfold('/prod/main').attr_foo == "main_attr"

def test_tree_unfold_full():
    tree = Tree()
    tree.set('/', attr={'attr_foo': 'bar', 'default': 'default_root'})
    tree.set('/prod', attr={'other_attr': 'foo'})
    tree.set('/prod/main', attr={'attr_foo': 'main_attr'})

    assert tree.unfold('/').attr_foo == "bar"
    assert tree.unfold('/').default == "default_root"

    assert tree.unfold('/prod').other_attr == "foo"
    assert tree.unfold('/prod').attr_foo == "bar"
    assert tree.unfold('/prod').default == "default_root"

    assert tree.unfold('/prod/main').attr_foo == 'main_attr'
    assert tree.unfold('/prod/main').other_attr == 'foo'
    assert tree.unfold('/prod/main').default == 'default_root'
