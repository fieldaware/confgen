import operator
from functools import reduce
import shutil
import os
from os.path import join
from collections import MutableMapping
import yaml

from . import inventory
from . import view

class Node(MutableMapping):
    def __init__(self, name, level, parent, root=None):
        self.name = name
        self.level = level
        self.parent = parent
        self.root = root or self
        self.children = dict()
        self.inventory = dict()

    def up(self):
        node = self
        while node is not None:  # root's parent is None.
            yield node
            node = node.parent

    @property
    def services(self):
        # XXX: refactor me please.
        def scan(node):
            if not node.has_children:
                yield node
            else:
                for child in node:
                    for i in scan(child):
                        yield i
        return [i for i in scan(self.root)]

    @property
    def path(self):
        return "/".join(reversed([str(i) for i in self.up()]))

    @property
    def has_children(self):
        return bool(self.children)

    def by_path(self, parts):
        return reduce(operator.getitem, parts, self.root)

    @property
    def flatten(self):
        def merge_dicts(x, y):
            '''
            if I only had python3.5 {**x, **y} :<
            '''
            c = y.inventory.copy()
            c.update(x)
            return c

        return reduce(merge_dicts, self.up(), self.inventory)

    def __repr__(self):
        return "Node <{}>: {}".format(id(self), self.name)

    def __str__(self):
        return self.name

    def __getitem__(self, key):
        return self.children[key]

    def __setitem__(self, key, value):
        self.children[key] = value

    def __iter__(self):
        return iter(self.children.values())

    def __len__(self):
        return len(self.children)

    def __delitem__(self, key):
        raise ValueError("Deletion not allowed")

    @property
    def as_dict(self):
        stages = {i.level: i for i in self.up()}
        stages.update(self.flatten)
        return stages

class ConfGen(object):
    build_dir = 'build'

    def __init__(self, home, config):
        self.home = home
        self.config = yaml.load(config)
        assert 'hierarchy' in self.config, "hierarchy list is required"
        assert 'service' in self.config, "service list is required"
        assert 'infra' in self.config, "infra tree is required"
        self.root = self.build_tree(self.config['infra'])
        self.inventory = inventory.Inventory(self.root, home)
        self.renderer = view.Renderer(home)

    def build_tree(self, infra):
        root = Node('infra', self.config['hierarchy'][0], None, None)

        def add_node(infra_sub, name, level, parent):
            node = Node(name, self.config['hierarchy'][level], parent, root)
            # add child to parent
            if parent is not None:
                parent[str(node)] = node
            for k in infra_sub:
                if not isinstance(infra_sub, MutableMapping):
                    add_node({}, k, level + 1, node)
                else:
                    add_node(infra_sub[k], k, level + 1, node)
        for k in infra:
            add_node(infra[k], k, 1, root)
        return root

    def collect(self):
        '''
        takes leafs from the tree and renders templates for them
        '''
        self.inventory.collect(self.tree)
        for leaf in self.tree.leafs:
            leaf.templates = self.renderer.service(leaf)

    def flush(self, collected):
        land_dir = join(self.home, self.build_dir)
        # remove all files to avoid stale configs (they will re-generated)
        try:
            shutil.rmtree(self.build_dir)
        except OSError as e:
            if e.errno == 2:  # build dir not found, it is fine, ignore
                pass
            else:
                raise

        for path, contents in collected.items():
            path = path.rstrip('/')  # remove '/' from the begging
            # create dirs if they don't exist
            inventory.mkdir_p(join(land_dir, os.path.dirname(path)))
            with open(join(land_dir, path), 'w+') as f:
                f.write(contents)

    def build(self):
        self.flush(self.collect())

    def set(self, path, key, value):
        self.inventory.set(path, key, value)

    def delete(self, path, key):
        self.inventory.delete(path, key)

    def search_key(self, pattern):
        result = self.inventory.search_key(pattern)
        return self.renderer.render_search_result(result)

    def search_value(self, pattern):
        result = self.inventory.search_value(pattern)
        return self.renderer.render_search_result(result)
