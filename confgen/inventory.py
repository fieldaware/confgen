import errno
import os
from os.path import join

import yaml

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class Inventory(object):
    inventory_delimiter = '/'
    config_filename = 'config.yaml'
    source_key_pattern = '{key}__source'

    def __init__(self, home=None):
        self.home = home
        self.inventory_dir = join(home, 'inventory')

    def _parse_file_path(self, path):
        '''
        takes absolute path in inventory and parses it relative
        '''
        relative_path = path[len(self.inventory_dir):]  # strip absolute path
        if relative_path == '':  # set root path as '/'
            return '/'
        return relative_path

    def collect(self):
        '''
        walks to home dir and collects yaml files
        '''
        inventory = {}
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename)))
                inventory[self._parse_file_path(path)] = configyml
        return inventory

    def set(self, path, key, value):
        '''
        add a value to the inventory and saves results to disk
        '''
        collected = self.collect()
        if path not in collected:
            collected[path] = {}
        collected[path][key] = value
        self._flush(collected)

    def delete(self, path, key):
        '''
        deletes keys/value pair from the inventory and saves results to disk
        '''
        collected = self.collect()
        if path not in collected:
            return
        if key in collected[path]:
            collected[path].pop(key)
        self._flush(collected)

    def _flush(self, inventory):
        '''
        saves given inventory to disk
        '''
        for path, contents in inventory.items():
            dst_dir = join(self.inventory_dir, path.strip('/'))
            mkdir_p(dst_dir)
            with open(join(dst_dir, self.config_filename), 'w+') as f:
                yaml.dump(contents, f, default_flow_style=False)

    def build(self):
        '''
        builds flat dict structure based on loaded files
        '''
        inventory = self.collect()
        return {path: self._build_single_row(inventory, path) for path in inventory}

    def invetory_for_path(self, inventory, path):
        for path in reversed(list(self.traverse(path))):
            candidate = inventory.get(path)
            if candidate:
                return candidate

    def traverse(self, path):
        '''
        takses a path and yields all its componenets from top to bottom

        / -> /
        /prod -> /, /prod
        /dev/qa1 -> /, /dev, /dev/qa1
        '''
        list_path = path.rstrip('/').split('/')
        for i in range(len(list_path)):
            yield '/'.join(list_path[:i + 1]) or '/'

    def _build_single_row(self, inventory, path):
        kv_set = {}
        for path in self.traverse(path):
            update_with = inventory.get(path, {})
            kv_set.update(update_with)

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
