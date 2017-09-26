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

    # def flatten(self, path):
    #     attrs = {}
    #     sources = defaultdict(list)
    #     for node in self.nodes(path):
    #         attrs.update(node.data)
    #         for overlap in set(attrs.keys()).intersection(set(node.data)):
    #             sources[overlap].append(node.full_path)
    #
    #     for key, appearnces in sources.items():
    #         if len(appearnces) == 1:
    #             attrs["{}__source".format(key)] = appearnces[0]
    #         else:
    #             attrs["{}__source".format(key)] = "{} override: {}".format(appearnces[0], ", ".join(appearnces[1:]))
    #     return Node(name=str(node), full_path=path, data=attrs)
    #
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
        return [i for i in path[len(self.inventory_dir) + 1:].split('/') if i]

    def __collect(self):
        """
        Walks to home dir and collects yaml files
        """
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename)))
                try:
                    self._tree.by_path(self._parse_file_path(path)).inventory = configyml
                except KeyError:
                    # something in the inventory that doesn't make sense
                    # a path that doesn't exist in the infra tree but is present
                    # in the inventory
                    pass

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
        return [n for n in self._tree.all() if rgx.search(n.path) and n.inventory]

    def search_value(self, pattern):
        rgx = re.compile(pattern)

        def lookup(n):
            for k, v in n.inventory.items():
                if rgx.search(k) or rgx.search(str(v)):  # v might be int or float
                    return n

        return [i for i in self._tree.all() if lookup(i)]
