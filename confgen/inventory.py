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

    def __getitem__(self, name):
        return self._dict[name]

    def __str__(self):
        return self._name

    def __repr__(self):
        return "<Node: {}> {}".format(id(self), self._name)

    def __iter__(self):
        return self._dict.values().__iter__()

    def __getattr__(self, name):
        try:
            return self._attrs[name]
        except KeyError as e:
            raise AttributeError(e)


class Tree(object):
    root_path = "."

    def __init__(self):
        self._root = Node(self.root_path)

    def add_node(self, keys, attr):
        node = Node(name=name, attributes=attr)
        to_add = self.safeget(*path)
        to_add[str(node)] = node

    def safeget(self, *keys):
        '''
        get a value from a nested dict
        '''
        if keys == [self.root_path, ]:
            return self._root
        ret = self._root
        for key in keys:
            try:
                ret = ret[key]
            except KeyError:
                return None
        return ret

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
        inventory = {}
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename)))
                inventory[self._parse_file_path(path)] = configyml
        return inventory

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

    def build(self, sources=True):
        """
        Builds flat dict structure based on loaded files
        """
        inventory = self.collect()
        return {path: self._build_single_row(inventory, path, sources) for path in inventory}

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

    @staticmethod
    def traverse(path):
        """
        Takes a path and yields all its componenets from top to bottom

        / -> /
        /prod -> /, /prod
        /dev/qa1 -> /, /dev, /dev/qa1
        """
        list_path = path.rstrip('/').split('/')
        for i in range(len(list_path)):
            yield '/'.join(list_path[:i + 1]) or '/'

    def _build_single_row(self, inventory, path, sources):
        kv_set = {}
        for path in self.traverse(path):
            update_with = inventory.get(path, {})
            kv_set.update(update_with)

        if sources:
            kv_set.update(self._track_invetory_source(inventory, path))
        return kv_set

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
