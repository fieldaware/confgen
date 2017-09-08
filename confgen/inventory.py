import re
import errno
import os
from os.path import join

import yaml


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if not exc.errno == errno.EEXIST:
            raise

class Node(object):
    def __init__(self, name='', nodes=(), attributes=None):
        self._name = name
        self._dict = {str(item): item for item in nodes}
        self._attrs = attributes or {}

    @property
    def has_children(self):
        return bool(self._dict)

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __getitem__(self, name):
        return self._dict[name]

    def __str__(self):
        return self._name

    def __repr__(self):
        return "<Node: {}> {}".format(id(self), self._name)

    def __iter__(self):
        return self._dict.values().__iter__()

    def update_attrs(self, attrs):
        self._attrs.update(attrs)

    @property
    def all_attrs(self):
        return self._attrs

    def __getattr__(self, name):
        try:
            return self._attrs[name]
        except KeyError as e:
            raise AttributeError(e)

class Tree(object):
    def __init__(self):
        self._root = Node(name='/')

    def get_built(self, path):

        def traverse(node, parent_node):
            print 'updating {} with attrs {} with {} with attrs {}'.format(node, node._attrs, parent_node, parent_node._attrs)
            node._attrs.update(parent_node._attrs)

            for child in node:
                traverse(child, node)
        traverse(self._root, self._root)

    def set(self, path, attr):
        if path == "/":
            self._root.update_attrs(attr)
        keys = path.strip('/').split('/')
        ret = self._root
        for i, key in enumerate(keys):
            try:
                ret = ret[key]
            except KeyError:
                if i + 1 == len(keys):
                    ret[key] = Node(name=key, attributes=attr)
                else:
                    ret[key] = Node(name=key)
                ret = ret[key]
        return ret

    def get(self, path):
        if path == "/":
            return self._root
        keys = path.strip('/').split('/')

        def traverse(parts, node):
            print parts, node
            if not parts:
                return node
            else:
                next_key, rest = parts[0], parts[1:]
                return traverse(rest, node[next_key])
        return traverse(keys, self._root)

    def unfold(self, path, sources=True):
        if path == "/":
            return self._root
        keys = path.strip('/').split('/')

        def traverse(parts, node):
            if not parts:
                return node
            else:
                next_key, rest = parts[0], parts[1:]
                n = node[next_key]
                for k,v in node._attrs.items():
                    if k not in n:
                        print 'updating {} with k: {} and v: {}'.format(n, k ,v)
                        n[k] = v

                return traverse(rest, n)
        return traverse(keys, self._root)

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
        tree = Tree()
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename)))
                tree.set(self._parse_file_path(path), configyml)
        return tree

    def set(self, path, key, value):
        """
        Add a value to the inventory and saves results to disk
        """
        collected = self.collect()
        if path not in collected:
            collected[path] = {}
        collected[path][key] = value
        self._flush(collected)

    def delete(self, path, key):
        """
        Deletes keys/value pair from the inventory and saves results to disk
        """
        collected = self.collect()
        if path not in collected:
            return
        if key in collected[path]:
            collected[path].pop(key)
        self._flush(collected)

    def _flush(self, inventory):
        """
        Saves given inventory to disk
        """
        for path, contents in inventory.items():
            dst_dir = join(self.inventory_dir, path.strip('/'))
            mkdir_p(dst_dir)
            with open(join(dst_dir, self.config_filename), 'w+') as f:
                yaml.safe_dump(contents, f, default_flow_style=False)

    def inventory_for_path(self, inventory, path):
        for path in reversed(list(self.traverse(path))):
            candidate = inventory.get(path)
            if candidate:
                return candidate

    def search_key(self, pattern):
        rgx = re.compile(pattern)
        inventory = self.build(sources=False)
        return {k: v for k, v in inventory.items() if rgx.search(k)}

    def search_value(self, pattern):
        rgx = re.compile(pattern)
        inventory = self.build(sources=False)

        def search():
            for path, inventory_entry in inventory.items():
                for entry_key, entry_value in inventory_entry.items():
                    if rgx.search(entry_key) or rgx.search(str(entry_value)):
                        yield path, {entry_key: entry_value}

        return {k: v for (k, v) in search()}

    def build(self, sources=True):
        inventory = self.collect()
        inventory.build()
        return inventory

    def _track_invetory_source(self, inventory, path):
        sources = {}
        for path in self.traverse(path):
            for k in inventory.get(path, {}):
                sources.setdefault(k, []).append(path)

        prefixed_source_vars = {
            Inventory.source_key_pattern.format(key=k):
                '{key}:{path}'.format(key=k, path=v[0]) + (' override:{paths}'.format(paths=','.join(v[1:])) if v[1:] else '')
            for k, v in sources.items()
        }
        return prefixed_source_vars
