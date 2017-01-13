import shutil
import os
from os.path import join
import yaml
import collections

import inventory
import view

def flatten_dict(d, parent_key='', sep='/'):
    '''
    Takes a nested dict such as
    {
        'foo': {
            'bar': {
                'lol':1
            }
        }
    }
    and converts it to
    {'/foo/bar/lol': 1}
    '''
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else sep + k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

class ConfGen(object):
    build_dir = 'build'

    def __init__(self, home, config):
        self.home = home
        self.config = yaml.load(config)
        self.inventory = inventory.Inventory(home)
        self.renderer = view.Renderer(self.config['service'], home)

    @property
    def flatten_infra(self):
        return flatten_dict(self.config['infra'])

    def merge_config_with_inventory(self):
        public_inventory = self.inventory.build()
        merged = {}
        for path, services in self.flatten_infra.items():
            for service in services:
                combined = join(path, service)
                merged[combined] = self.inventory.invetory_for_path(public_inventory, combined)
        return merged

    def collect(self):
        config_with_inventory = self.merge_config_with_inventory()
        config_with_redered_templates = {}
        for path, inventory_for_path in config_with_inventory.items():
            for filename, contents in self.renderer.render_templates(path, inventory_for_path).items():
                config_with_redered_templates[join(path, filename)] = contents
        return config_with_redered_templates

    def flush(self, collected):
        land_dir = join(self.home, self.build_dir)
        # remove all files to avoid stale configs (they will be re-generated)
        shutil.rmtree(self.build_dir, ignore_errors=True)
        for path, contents in collected.items():
            path = path.strip('/')  # remove '/' from the beginning
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
