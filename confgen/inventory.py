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
    def __init__(self, name='', nodes=(), attributes=None):
        self._name = name
        self._nodes = {str(item): item for item in nodes}
        self._attrs = attributes or {}

    @property
    def has_children(self):
        return bool(self._nodes)

    def __setitem__(self, key, value):
        self._nodes[key] = value

    def __getitem__(self, key):
        return self._nodes[key]

    def setdefault(self, key, value):
        try:
            return self._nodes[key]
        except KeyError:
            self._nodes[key] = value
        return value

    def __str__(self):
        return self._name

    def __repr__(self):
        return "<Node: {}> {}".format(id(self), self._name)

    def __iter__(self):
        return self._nodes.values().__iter__()

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

class DB(object):
    def __init__(self):
        self._root = Node(name='/')

    def nodes(self, path):
        yield self._root
        if path == "/":
            raise StopIteration
        parts = path.strip('/').split('/')
        node = self._root
        for part in parts:
            node = node[part]
            yield node

    def set(self, path, attrs):
        if path == "/":
            self._root.update_attrs(attrs)
        parts = path.strip('/').split('/')

        node = self._root
        for part in parts:
            # Get (or create Node)
            node = node.setdefault(part, Node(name=part))

        # set the attrs on the final node (i.e. the end of path)
        node.update_attrs(attrs)

    def get(self, path):
        # return the last node on the path
        return list(self.nodes(path))[-1]

    def flatten(self, path, sources=True):
        attrs = {}
        sources = defaultdict(list)
        full_path = ""
        for node in self.nodes(path):
            full_path = os.path.join(full_path, str(node))
            attrs.update(node.all_attrs)
            for overlap in set(attrs.keys()).intersection(set(node.all_attrs)):
                sources[overlap].append(full_path)

        for key, appearnces in sources.items():
            if len(appearnces) == 1:
                attrs["{}__source".format(key)] = appearnces[0]
            else:
                attrs["{}__source".format(key)] = "{} override: {}".format(appearnces[0], ", ".join(appearnces[1:]))
        return Node(name=str(node), attributes=attrs)

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
