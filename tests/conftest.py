import shutil
import tempfile
import yaml
import os
from click.testing import CliRunner
import pytest
from confgen.view import Renderer
from confgen.logic import ConfGen

pwd = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def simplerepo(request):
    rootdir = tempfile.mkdtemp()
    simplerepo_dst = os.path.join(rootdir, 'simplerepo')
    shutil.copytree(os.path.join(pwd, 'simplerepo'), simplerepo_dst)
    return simplerepo_dst


@pytest.fixture
def confgenyaml(simplerepo, request):
    return yaml.load(open(os.path.join(simplerepo, 'confgen.yaml')))


@pytest.fixture
def runner(confgenyaml):
    runner = CliRunner()
    return runner


@pytest.fixture
def inventory(confgen):
    return confgen.inventory


@pytest.fixture
def renderer(confgenyaml, inventory, simplerepo):
    return Renderer(home=simplerepo)


@pytest.fixture
def confgen(request, simplerepo):
    return ConfGen(home=simplerepo, config=open(os.path.join(simplerepo, 'confgen.yaml')))
