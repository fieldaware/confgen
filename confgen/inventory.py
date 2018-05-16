import re
import errno
import os
from os.path import join

import yaml

from . import dir_rm

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if not exc.errno == errno.EEXIST:
            raise

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

    def __init__(self, tree, home=None):
        self.home = home
        self.inventory_dir = join(home, 'inventory')
        self._tree = tree
        self.__collect()

    def _parse_file_path(self, path):
        """
        Takes absolute path in inventory and parses it relative
        """
        return path[len(self.inventory_dir):]

    def __collect(self):
        """
        Walks to home dir and collects yaml files
        """
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename))) or {}
                try:
                    self._tree.by_path(self._parse_file_path(path)).inventory = configyml
                except KeyError:
                    # XXX
                    # something in the inventory that doesn't make sense
                    # a path that doesn't exist in the infra tree but is present
                    # in the inventory
                    pass

    def set(self, path, key, value):
        """
        Add a value to the inventory and saves results to disk
        """
        self._tree.by_path(path).inventory[key] = value
        self._flush()

    def delete(self, path, key):
        """
        Deletes keys/value pair from the inventory and saves results to disk
        """
        try:
            deleted = self._tree.by_path(path).inventory.pop(key)
        except KeyError:  # node or key cannot be found
            return
        self._flush()
        return deleted

    def _flush(self):
        """
        Saves current inventory to disk
        """
        dir_rm(self.inventory_dir)
        for node in (i for i in self._tree.all() if i.inventory):
            # XXX: this infra/ bugs me
            dst_dir = join(self.inventory_dir, node.path.lstrip('/'))
            mkdir_p(dst_dir)
            with open(join(dst_dir, self.config_filename), 'w+') as f:
                yaml.safe_dump(node.inventory, f, default_flow_style=False)

    def search_key(self, pattern):
        rgx = re.compile(pattern)
        return [(n.path, n.inventory) for n in self._tree.all() if rgx.search(n.path) and n.inventory]

    def search_value(self, pattern):
        rgx = re.compile(pattern)

        def lookup():
            for n in self._tree.all():
                for k, v in n.inventory.items():
                    if rgx.search(k) or rgx.search(str(v)):  # v might be int or float
                        yield n.path, {k: v}

        return list(lookup())
