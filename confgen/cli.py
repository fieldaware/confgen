import click
import yaml
import os

class ConfigTool(object):
    def __init__(self, home=None, config=None):
        self.home = home
        self.config = yaml.load(open(config))
        self.configdata_dir = os.path.join(home, 'configdata')

    def load(self):
        '''
        walks to home dir and collects yaml files
        '''
        struct = {}
        for path, dirs, files in [i for i in os.walk(os.path.join(self.home, 'kvstore'))]:
            if files:
                struct[os.path.basename(path)] = yaml.load(open(os.path.join(path, 'config.yaml')))

    def build(self):
        '''
        builds the structure based on loaded files
        '''
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
