import errno
import click
import yaml
from jinja2 import Environment, FileSystemLoader
import os
from os.path import join, isfile
import logging
import collections

logging.getLogger('confgen').addHandler(logging.StreamHandler())
log = logging.getLogger('confgen')

class ConfGenError(Exception):
    pass


def flatten_dict(d, parent_key='', sep='/'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else sep + k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

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

    def __init__(self, home=None):
        self.home = home
        self.inventory_dir = join(home, 'inventory')

    def collect(self):
        '''
        walks to home dir and collects yaml files
        '''
        inventory = {}
        for path, dirs, files in os.walk(self.inventory_dir):
            if files:
                configyml = yaml.load(open(join(path, self.config_filename)))
                inventory['/' + path[len(self.inventory_dir) + 1:]] = configyml
        return inventory

    def set(self, path, key, value):
        collected = self.collect()
        if path not in collected:
            collected[path] = {}
        collected[path][key] = value
        self.flush(collected)

    def flush(self, inventory):
        for path, contents in inventory.items():
            dst_dir = join(self.inventory_dir, path.strip('/'))
            mkdir_p(dst_dir)
            yaml.dump(contents, open(join(dst_dir, self.config_filename), 'w+'))

    def build(self):
        '''
        builds flat dict structure based on loaded files
        '''
        inventory = self.collect()
        public_inventory = {}

        for path in sorted(inventory.keys()):
            list_path = path.strip('/').split('/')
            kv_set = inventory.get('/').copy()
            for i in range(len(list_path)):
                update_with_path = '/' + '/'.join(list_path[:i + 1])
                update_with = inventory.get(update_with_path, {})
                kv_set.update(update_with)
            public_inventory[path] = kv_set
        return public_inventory


class Renderer(object):
    templates_dir = 'templates'

    def __init__(self, services, home):
        self.home = home
        self.jinja_environ = Environment(loader=FileSystemLoader(join(home, self.templates_dir)))
        self.templates = self.collect_templates(services)

    def collect_templates(self, services):
        templates = {}
        for service in services:
            service_template_dir = join(self.home, self.templates_dir, service)
            templates[service] = [join(service, f) for f in os.listdir(service_template_dir) if isfile(join(service_template_dir, f))]
        return templates

    def render_multiple_templates(self, services, template_inventory):
        renders = {}
        for service in services:
            renders.update(self.render_templates(service, template_inventory))
        return renders

    def render_templates(self, service, template_inventory):
        renders = {}
        for template in self.templates[service]:
            renders[template] = self.jinja_environ.get_template(template).render(template_inventory)
        return renders

class ConfGen(object):
    build_dir = 'build'

    def __init__(self, home, config):
        self.home = home
        self.config = yaml.load(config)
        self.inventory = Inventory(home)
        self.renderer = Renderer(self.config['service'], home)

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

@click.group()
@click.option('--ct-home', envvar='CG_HOME', default='.',
              type=click.Path(exists=True, file_okay=False, resolve_path=True),
              help='The config home - typically your config git repo')
@click.option('--config', default='confgen.yaml', envvar='CG_CONFIG',
              help='Defaults to configtool.yaml in current directory',
              type=click.File('r'))
@click.pass_context
def cli(ctx, ct_home, config):
    ctx.obj = ConfGen(ct_home, config)

@cli.group()
def search():
    pass

@search.command()
@click.argument('pattern')
def key(pattern):
    click.echo("will search key " + pattern)

@search.command()
@click.argument('pattern')
def value(pattern):
    click.echo("will search value " + pattern)

@cli.command()
@click.pass_obj
def build(ctx):
    ctx.build()


@cli.command()
@click.argument('path')
@click.argument('key')
@click.argument('value')
@click.pass_obj
def set(ctx, path, key, value):
    ctx.set(path, key, value)


@cli.command()
@click.argument('path')
@click.argument('key')
def delete(path, key):
    click.echo("will delete the key: {} at path: {}".format(path, key))

@cli.command()
def lint():
    click.echo("will lint templates")

if __name__ == "__main__":
    cli()
