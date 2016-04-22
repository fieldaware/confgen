import yaml
import os
from click.testing import CliRunner
import pytest
from confgen.cli import Inventory, Renderer, ConfGen

pwd = os.path.dirname(os.path.abspath(__file__))

simplerepo = lambda x: os.path.join(os.path.join(pwd, 'simplerepo'), x)


@pytest.fixture
def confgenyaml(request):
    return yaml.load(open(simplerepo('confgen.yaml')))

@pytest.fixture
def runner(confgenyaml):
    runner = CliRunner()
    return runner

@pytest.fixture
def inventory():
    return Inventory(home=simplerepo('.'))

@pytest.fixture
def renderer(confgenyaml, inventory):
    return Renderer(confgenyaml['service'], home=simplerepo('.'))

@pytest.fixture
def confgen(request):
    return ConfGen(home=simplerepo('.'), config=open(simplerepo('confgen.yaml')))
