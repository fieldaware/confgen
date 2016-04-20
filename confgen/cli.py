import click
import yaml
from jinja2 import Template, Environment, FileSystemLoader
import os
from os.path import join, isfile
from collections import defaultdict


class ConfGenError(Exception):
    pass


def Tree():
    return defaultdict(Tree)


class Inventory(object):
    key_value_tag = "__kvs__"

    def __init__(self, home=None):
        self.home = home
        self.inventory_dir = os.path.join(home, 'inventory')

    def collect(self):
        '''
        walks to home dir and collects yaml files
        '''
        inventory = Tree()
        rootdir = self.inventory_dir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):  # os.walk you tried to be fun, you are not
            folders = path[start:].split(os.sep)
            parent = reduce(dict.get, folders[:-1], inventory)
            if files:
                configyml = yaml.load(open(os.path.join(path, 'config.yaml')))
                node = Tree()
                node.update({self.key_value_tag: configyml})
                parent[folders[-1]] = node
            else:
                parent[folders[-1]] = Tree()
        return inventory['inventory']

    def build(self):
        '''
        builds the structure based on loaded files
        '''
        inventory = self.collect()

        def _build(current_lvl, kvs):
            '''
            Recursively update each node
            '''
            if not any([isinstance(v, dict) for v in current_lvl.values()]):
                return

            current_kvs = current_lvl.pop(self.key_value_tag, {})
            kvs_copy = kvs.copy()
            kvs_copy.update(current_kvs)
            current_lvl[self.key_value_tag] = kvs_copy

            for k in current_lvl.keys():
                _build(current_lvl[k], kvs_copy)

        _build(inventory, {})
        return inventory


class Renderer(object):
    templates_dir = 'templates'

    def __init__(self, services, home):
        self.home = home
        self.jinja_environ = Environment(loader=FileSystemLoader(os.path.join(home, self.templates_dir)))
        self.templates = self.collect_templates(services)

    def collect_templates(self, services):
        templates = {}
        for service in services:
            service_template_dir = join(self.home, self.templates_dir, service)
            templates[service] = [join(service, f) for f in os.listdir(service_template_dir) if isfile(join(service_template_dir, f))]
        return templates

    def render_templates(self, service, template_inventory):
        renders = {}
        for template in self.templates[service]:
            renders[template] = self.jinja_environ.get_template(template).render(template_inventory)
        return renders

class ConfGen(object):
    def __init__(self, home, config):
        self.home = home
        self.config = yaml.load(open(config))
        self.inventory = Inventory(home)
        self.renderer = Renderer(self.inventory, config, home)


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
@click.pass_context
def build(ctx):
    click.echo("will build the templates")

@cli.command()
@click.argument('path')
@click.argument('key')
@click.argument('value')
def set(path, key, value):
    click.echo("will set the value: {}, at key: {} and path:{}".format(value, key, path))

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
