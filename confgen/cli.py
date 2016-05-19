import click
import logging

from logic import ConfGen

logging.getLogger('confgen').addHandler(logging.StreamHandler())
log = logging.getLogger('confgen')

class ConfGenError(Exception):
    pass

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
@click.pass_obj
def key(ctx, pattern):
    print ctx.search_key(pattern)

@search.command()
@click.argument('pattern')
@click.pass_obj
def value(ctx, pattern):
    print ctx.search_value(pattern)

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
@click.pass_obj
def delete(ctx, path, key):
    ctx.delete(path, key)

@cli.command()
def lint():
    click.echo("will lint templates")

if __name__ == "__main__":
    cli()
