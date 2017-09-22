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

    @property
    def path(self):
        def up(node, acc=None):
            acc = acc or []
            acc.insert(0, str(node))
            if node.parent:
                return up(node.parent, acc)
            return acc

        return "/".join(up(self))

    @property
    def is_child(self):
        return bool(self.children)

    def by_path(self, parts):
        return reduce(operator.getitem, parts, self)

    def find_source(self, key):
        def up(node):
            if node is None:
                raise KeyError("Key: {} not found in the tree")
            if node.inventory.get(key):
                return node.path
            else:
                return up(node.parent)
        return up(self)

    def flatten(self, key):
        def up(node):
            if node is None:
                raise KeyError("Key: {} not found in the tree")
            return node.inventory.get(key) or up(node.parent)
        return up(self)

    def __repr__(self):
        return "Node <{}>: {}".format(id(self), self.name)

    def __str__(self):
        return self.name

    def __getitem__(self, key):
        # FIXME
        # self.children.get(key, self.inventory[key]) doesnt work ;x
        try:
            return self.children[key]
        except KeyError:
            return self.flatten(key)

    def __setitem__(self, key, value):
        self.children[key] = value

    def __iter__(self):
        return iter(self.children.values())

    def __len__(self):
        return len(self.children)

    def __delitem__(self, key):
        raise ValueError("Deletion not allowed")

    @property
    def leafs(self):
        acc = []
        def down(node):
            if not node.is_child:
                acc.append(node)
            else:
                for c in node:
                    down(c)
        down(self)
        return acc

    @property
    def as_dict(self):
        def up(node, acc=None):
            acc = acc or []
            acc.insert(0, node)
            if node.parent:
                return up(node.parent, acc)
            return acc

        def down(node, path, acc=None):
            acc = acc or {}
            acc.update(node.inventory)
            if node.get(path[0]):
                return down(node.get(path[0]), path[1:], acc)
            return acc

        stages = {s.level: s for s in up(self)}
        stages.update(down(self.root, self.path.split('/')))
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
        self.inventory = inventory.Inventory(home)
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


    def add_inventory(self):
        pass

    def add_templates(self):
        pass

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
