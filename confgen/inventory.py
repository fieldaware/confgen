import re
import errno
import os
from os.path import join

from collections import defaultdict

import yaml


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if not exc.errno == errno.EEXIST:
            raise

class Node(object):
    """
        a <Node> for a tree
        
        Nodes have a name, children and data (attributes)

        Name is specified in the constructor:
            node = Node("my_node_name")

        Name is read via:
            str(node)

        Data is specified in the constructor:
            node = Node("my_node", data={'my_data_attr', 'my data value'})

        Data is read via attribute access:
            node.my_data_attr

        Children can be added in the constructor:
            node = Node("my_node", children=(child_node_1, child_node_2, child_node_N))

        Children can be added via the dict interface:
            node['my_child_node'] = Node('my_child_node')

        Children can be looked up by their name, in the parent node:
            child_node = parent_node['child_nodes_name']

    """
    def __init__(self, name, full_path="", children=(), data=None):
        self._name = name
        self.full_path = full_path
        self._children = {str(child): child for child in children}
        self._data = data or {}

    @property
    def has_children(self):
        return bool(self._children)

    def __setitem__(self, key, value):
        self._children[key] = value

    def __getitem__(self, key):
        return self._children[key]

    def setdefault(self, key, value):
        try:
            return self._children[key]
        except KeyError:
            self._children[key] = value
        return value

    def __str__(self):
        return self._name

    def __repr__(self):
        return "<Node: {}> {}".format(id(self), self._name)

    def __iter__(self):
        return self._children.values().__iter__()

    def update_data(self, data):
        self._data.update(data)

    @property
    def data(self):
        return self._data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError as e:
            raise AttributeError(e)

class DB(object):
    def __init__(self):
        self._root = Node(name='/', full_path="/")

    def all_nodes(self, node=None):
        if node is None:
            node = self._root
        yield node
        for child in node:
            # force generator to yield the childs
            for i in self.all_nodes(node=child):
                yield i

    def nodes(self, path):
        yield self._root
        if path == "/":
            raise StopIteration
        parts = path.strip('/').split('/')
        node = self._root
        for part in parts:
            try:
                node = node[part]
            # best effor to deliver the path
            # if the path is not complete stop there.
            # this might be an ugly shortcut.
            except KeyError:
                break
            yield node

    def set(self, path, attrs):
        if path == "/":
            self._root.update_data(attrs)
        parts = path.strip('/').split('/')

        node = self._root
        full_path = self._root.full_path
        for part in parts:
            # Get (or create Node)
            full_path = os.path.join(full_path, part)
            node = node.setdefault(part, Node(part, full_path=full_path))

        # set the attrs on the final node (i.e. the end of path)
        node.update_data(attrs)

    def get(self, path):
        # return the last node on the path
        try:
            return list(self.nodes(path))[-1]
        except KeyError:
            return

    def flatten(self, path):
        attrs = {}
        sources = defaultdict(list)
        for node in self.nodes(path):
            attrs.update(node.data)
            for overlap in set(attrs.keys()).intersection(set(node.data)):
                sources[overlap].append(node.full_path)

        for key, appearnces in sources.items():
            if len(appearnces) == 1:
                attrs["{}__source".format(key)] = appearnces[0]
            else:
                attrs["{}__source".format(key)] = "{} override: {}".format(appearnces[0], ", ".join(appearnces[1:]))
        return Node(name=str(node), full_path=path, data=attrs)

class Inventory(object):
    """
    Represents, builds and saves the invetory.

    It is represented as a directory structure for easy managment.
    Diffs for single file would be hard to read and maintain, while single files
    are trivial to manage.
    """
    inventory_delimiter = '/'
    config_filename = 'config.yaml'
    source_key_pattern = '{key}__source'

    def __init__(self, home=None):
        self.home = home
        self.inventory_dir = join(home, 'inventory')

    def _parse_file_path(self, path):
        """
        Takes absolute path in inventory and parses it relative
        """
        relative_path = path[len(self.inventory_dir):]  # strip absolute path
        if relative_path == '':  # set root path as '/'
            return '/'
        return relative_path

    def collect(self):
        """
        Walks to home dir and collects yaml files
        """
        db = DB()
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename)))
                db.set(self._parse_file_path(path), configyml)
        return db

    def set(self, path, key, value):
        """
        Add a value to the inventory and saves results to disk
        """
        db = self.collect()
        db.set(path, {key: value})
        self._flush(db)

    def delete(self, path, key):
        """
        Deletes keys/value pair from the inventory and saves results to disk
        """
        db = self.collect()
        item = db.get(path)
        if not item:
            return
        attrs = item.data
        try:
            attrs.pop(key)
        except KeyError:
            return
        db.set(path, attrs)
        self._flush(db)

    def _flush(self, inventory):
        """
        Saves given inventory to disk
        """
        i = {n.full_path: n.data for n in inventory.all_nodes() if n.data}
        for path, contents in i.items():
            dst_dir = join(self.inventory_dir, path.strip('/'))
            mkdir_p(dst_dir)
            with open(join(dst_dir, self.config_filename), 'w+') as f:
                yaml.safe_dump(contents, f, default_flow_style=False)

    def search_key(self, pattern):
        rgx = re.compile(pattern)
        all_nodes = self.collect().all_nodes()
        return {n.full_path: n.data for n in all_nodes if rgx.search(n.full_path) and n.data}

    def search_value(self, pattern):
        rgx = re.compile(pattern)
        all_nodes = {n.full_path: n.data for n in self.collect().all_nodes() if n.data}

        def search():
            for path, inventory_entry in all_nodes.items():
                for entry_key, entry_value in inventory_entry.items():
                    if rgx.search(entry_key) or rgx.search(str(entry_value)):
                        yield path, {entry_key: entry_value}

        return {k: v for (k, v) in search()}
