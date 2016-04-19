import click
import yaml
import os
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
    def __int__(self, inventory, home):
        self.inventory = inventory
        self.templates_dir = os.path.join(home, 'templates')

    def render(self):
        pass

    def flush(self):
        '''
        flushes builded structure to a disk
        '''
        pass


@click.group()
@click.option('--ct-home', envvar='CG_HOME', default='.',
              type=click.Path(exists=True, file_okay=False, resolve_path=True),
              help='The config home - typically your config git repo')
@click.option('--config', default='configtool.yaml', envvar='CG_CONFIG',
              help='Defaults to configtool.yaml in current directory',
              type=click.File('r'))
@click.pass_context
def cli(ctx, ct_home, config):
    ctx.obj = ConfigTool(ct_home, config)

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
