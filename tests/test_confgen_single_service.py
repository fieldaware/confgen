import pytest
from os.path import join


def test_confgen_tree_build(confgen_single_service):
    '''
    Based on:
    hierarchy:
    - GLOBAL
    - STAGE
    - CLUSTER

    infra:
    prod: # stage
        - main # cluster
        - multiapp # cluster
        - staging  # cluster

    dev: # stage
        - qa1 # cluster
        - qa2 # cluster
    '''
    t = confgen_single_service.root

    # test Nodes
    assert t.name == "/"
    assert t.level == "GLOBAL"
    assert t.parent is None
    assert set([str(c) for c in t]) == {'dev', 'prod'}

    assert t['prod'].name == "prod"
    assert t['prod'].level == "STAGE"
    assert t['prod'].parent is t
    assert set([str(c) for c in t['prod']]) == {'main', 'multiapp', 'staging'}

    assert t['prod']['main'].name == "main"
    assert t['prod']['main'].level == "CLUSTER"
    assert t['prod']['main'].parent is t['prod']

    assert t['prod']['multiapp'].name == "multiapp"
    assert t['prod']['multiapp'].level == "CLUSTER"
    assert t['prod']['multiapp'].parent is t['prod']

    assert t['prod']['staging'].name == "staging"
    assert t['prod']['staging'].level == "CLUSTER"
    assert t['prod']['staging'].parent is t['prod']

    assert t['dev'].name == "dev"
    assert t['dev'].level == "STAGE"
    assert t['dev'].parent is t

    assert t['dev']['qa1'].name == "qa1"
    assert t['dev']['qa1'].level == "CLUSTER"
    assert t['dev']['qa1'].parent is t['dev']

    assert t['dev']['qa2'].name == "qa2"
    assert t['dev']['qa2'].level == "CLUSTER"
    assert t['dev']['qa2'].parent is t['dev']


def test_confgen_tree_path(confgen_single_service):
    confgen = confgen_single_service
    assert confgen.root['prod']['main'].path == "/prod/main"
    assert confgen.root['dev']['qa1'].path == "/dev/qa1"
    assert confgen.root.path == "/"


def test_confgen_paths(confgen_single_service):
    confgen = confgen_single_service
    assert confgen.root.path == '/'
    assert confgen.root['prod'].path == "/prod"
    assert confgen.root['dev'].path == "/dev"
    assert confgen.root['prod']['main'].path == "/prod/main"
    assert confgen.root['dev']['qa1'].path == "/dev/qa1"
    assert confgen.root['dev']['qa2'].path == '/dev/qa2'


@pytest.mark.parametrize('path,expected', (
    ('', []),
    ('/', []),
    ('/prod', ['prod']),
    ('/prod/main', ['prod', 'main'])
))
def test_path_to_list(confgen_single_service, path, expected):
    confgen = confgen_single_service
    assert confgen.root.path_to_list(path) == expected


def test_confgen_tree_by_path(confgen_single_service):
    confgen = confgen_single_service
    assert confgen.root.by_path("/") is confgen.root
    assert confgen.root.by_path("") is confgen.root
    assert confgen.root.by_path("/dev/qa1") is confgen.root['dev']['qa1']


def test_confgen_tree_leaves(confgen_single_service):
    assert set([i.path for i in confgen_single_service.root.leaves]) == {
        '/prod/main',
        '/prod/multiapp',
        '/prod/staging',
        '/dev/qa1',
        '/dev/qa2',
    }


def test_confgen_build(confgen_single_service):
    confgen = confgen_single_service
    confgen.build()

    def f(p): return open(join(confgen.home, confgen.build_dir, p)).read()
    assert f('dev/qa1/my.cnf') == "/ dev qa1"
    assert f('dev/qa1/production.ini') == "4.0 password qa1 qa2"
    assert f('dev/qa2/my.cnf') == "/ dev qa2"
    assert f('dev/qa2/production.ini') == "9.0 password qa1 qa2"
    assert f('prod/main/my.cnf') == "/ prod main"
    assert f('prod/main/production.ini') == "3.0 password main multiapp staging"
    assert f('prod/multiapp/my.cnf') == "/ prod multiapp"
    assert f('prod/multiapp/production.ini') == "2.0 password main multiapp staging"
    assert f('prod/staging/my.cnf') == "/ prod staging"
    assert f('prod/staging/production.ini') == "2.0 password main multiapp staging"
