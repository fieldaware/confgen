import shutil
import os
from os.path import join
import yaml
import copy
import collections

from . import inventory
from . import view


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
    hierarchy_key = "_hierarchy"
    global_key = "_global"

    def __init__(self, home, config):
        self.home = home
        self.config = yaml.load(config)
        assert 'hierarchy' in self.config, "hierarchy list is required"
        assert 'service' in self.config, "service list is required"
        self.inventory = inventory.Inventory(home)
        self.renderer = view.Renderer(self.config['service'], home)

    @property
    def flatten_infra(self):
        return flatten_dict(self.config['infra'])

    def hierarchy_for_path(self, path):
        if path == "/" or path == "":
            return {}
        return dict(zip(self.config['hierarchy'], path.split('/')[1:]))

    def merge_config_with_inventory(self):
        public_inventory = self.inventory.build()
        merged = {path: copy.deepcopy(self.inventory.inventory_for_path(public_inventory, path)) for path in self.flatten_infra}
        _global = copy.deepcopy(merged)
        for path in merged:
            merged[path][self.hierarchy_key] = self.hierarchy_for_path(path)
            merged[path][self.global_key] = _global
        return merged

    def collect(self):
        config_with_inventory = self.merge_config_with_inventory()
        config_with_redered_templates = {}
        for path, services in self.flatten_infra.items():
            rendered_templates = self.renderer.render_templates_for_services(services, config_with_inventory[path])
            for template_path, config in rendered_templates.items():
                config_with_redered_templates['{}/{}'.format(path, template_path)] = config
        return config_with_redered_templates

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
            path = path.strip('/')  # remove '/' from the begging
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
