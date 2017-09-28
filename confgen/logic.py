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
    path_delimiter = "/"

    def __init__(self, name, level, parent, root=None):
        self.name = name
        self.level = level
        self.parent = parent
        self.root = root or self
        self.children = dict()
        self.inventory = dict()

    def all(self):
        # XXX: my spider senses are saying this could be implemented better
        yield self.root
        pending = [self.root, ]
        while pending:
            for child in pending.pop(0):
                yield child
                if child.has_children:
                    pending.append(child)

    def up(self):
        node = self
        while node is not None:  # root's parent is None.
            yield node
            node = node.parent

    @property
    def services(self):
        return [i for i in self.all() if not i.has_children]

    @property
    def path(self):
        return self.path_delimiter.join(reversed([str(i) for i in self.up()]))

    @property
    def has_children(self):
        return bool(self.children)

    def path_to_list(self, path):
        if path in ('', 'infra'):
            return []
        return path.lstrip('infra/').split(self.path_delimiter)

    def by_path(self, path):
        return reduce(operator.getitem, self.path_to_list(path), self.root)

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

    def rendered(self):
        for service in self.root.services:
            yield service, self.renderer.service(service)

    def build(self):
        land_dir = join(self.home, self.build_dir)
        # remove all files to avoid stale configs (they will re-generated)
        try:
            shutil.rmtree(self.build_dir)
        except OSError as e:
            if e.errno == 2:  # build dir not found, it is fine, ignore
                pass
            else:
                raise

        for node, rendered_tempaltes in self.rendered():
            dst_dir = join(land_dir, node.path.lstrip('infra/'))
            # create dirs if they don't exist
            inventory.mkdir_p(dst_dir)
            for filename, rendered_config in rendered_tempaltes.items():
                with open(join(dst_dir, filename), 'w+') as f:
                    f.write(rendered_config)

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
