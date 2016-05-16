import os
from os.path import join
import yaml
import collections

import inventory
import view

def flatten_dict(d, parent_key='', sep='/'):
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

    def merge_config_with_inventory(self):
        public_inventory = self.inventory.build()
        flatten_config = flatten_dict(self.config['infra'])

        built_config = {}
        for path, _ in flatten_config.items():
            # not pythonic yet, but feel free to do it better
            i = 0
            collected = {}
            while not collected.get(path):
                path_to_get = path.rsplit('/', i)[0]
                if not path_to_get:
                    path_to_get = '/'
                inventory_for_path = public_inventory.get(path_to_get)
                if inventory_for_path:
                    collected[path] = inventory_for_path
                else:
                    i += 1
            built_config[path] = collected[path]
        return built_config

    def collect(self):
        config_with_inventory = self.merge_config_with_inventory()
        config_with_redered_templates = {}
        for path, service in flatten_dict(self.config['infra']).items():
            rendered_templates = self.renderer.render_multiple_templates(service, config_with_inventory[path])
            for template_path, config in rendered_templates.items():
                config_with_redered_templates['{}/{}'.format(path, template_path)] = config
        return config_with_redered_templates

    def flush(self, collected):
        land_dir = join(self.home, self.build_dir)
        for path, contents in collected.items():
            path = path.strip('/')
            if not os.path.exists(join(land_dir, os.path.dirname(path))):
                os.makedirs(join(land_dir, os.path.dirname(path)))
            with open(join(land_dir, path), 'w+') as f:
                f.write(contents)

    def build(self):
        self.flush(self.collect())

    def set(self, path, key, value):
        self.inventory.set(path, key, value)

    def delete(self, path, key):
        self.inventory.delete(path, key)
