import pytest
from os.path import join

def test_confgen_tree_build(confgen):
    '''
    Based on:
    hierarchy:
      - GLOBAL
      - STAGE
      - CLUSTER
      - SERVICE

    infra:
      prod: # stage
        main: # cluster
          - webapp # service
        multiapp: # cluster
          *services # service
        staging:  # cluster
          *services # service

      dev: # stage
        qa1: # clusttreeer
          *services # service
        qa2: # cluster
          *services # service

    '''
    t = confgen.root

    # test Nodes
    assert t.name == "infra"
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
    assert [str(c) for c in t['prod']['main']] == ['webapp', ]

    assert t['prod']['multiapp'].name == "multiapp"
    assert t['prod']['multiapp'].level == "CLUSTER"
    assert t['prod']['multiapp'].parent is t['prod']
    assert set([str(c) for c in t['prod']['multiapp']]) == {'webapp', 'api'}

    assert t['prod']['staging'].name == "staging"
    assert t['prod']['staging'].level == "CLUSTER"
    assert t['prod']['staging'].parent is t['prod']
    assert set([str(c) for c in t['prod']['staging']]) == {'webapp', 'api'}

    assert t['dev'].name == "dev"
    assert t['dev'].level == "STAGE"
    assert t['dev'].parent is t
    assert set([str(c) for c in t['dev']]) == {'qa1', 'qa2'}

    assert t['dev']['qa1'].name == "qa1"
    assert t['dev']['qa1'].level == "CLUSTER"
    assert t['dev']['qa1'].parent is t['dev']
    assert set([str(c) for c in t['dev']['qa1']]) == {'webapp', 'api'}

    assert t['dev']['qa2'].name == "qa2"
    assert t['dev']['qa2'].level == "CLUSTER"
    assert t['dev']['qa2'].parent is t['dev']
    assert set([str(c) for c in t['dev']['qa2']]) == {'webapp', 'api'}

    # test Leafs
    assert t['prod']['main']['webapp'].name == "webapp"
    assert t['prod']['main']['webapp'].level == "SERVICE"
    assert t['prod']['main']['webapp'].parent is t['prod']['main']

    assert t['dev']['qa2']['api'].name == 'api'
    assert t['dev']['qa2']['api'].level == "SERVICE"
    assert t['dev']['qa2']['api'].parent is t['dev']['qa2']

def test_confgen_tree_path(confgen):
    assert confgen.root['prod']['main']['webapp'].path == "infra/prod/main/webapp"
    assert confgen.root['dev']['qa1']['api'].path == "infra/dev/qa1/api"
    assert confgen.root['prod']['main'].path == "infra/prod/main"
    assert confgen.root['dev']['qa1'].path == "infra/dev/qa1"
    assert confgen.root.path == "infra"

@pytest.mark.parametrize('path,expected', (
    ('', []),
    ('infra', []),
    ('infra/prod', ['prod']),
    ('infra/prod/main/webapp', ['prod', 'main', 'webapp'])
))
def test_path_to_list(confgen, path, expected):
    assert confgen.root.path_to_list(path) == expected

def test_confgen_tree_by_path(confgen):
    assert confgen.root.by_path("infra") is confgen.root
    assert confgen.root.by_path("infra/dev/qa1") is confgen.root['dev']['qa1']
    assert confgen.root.by_path('infra/dev/qa1/webapp') is confgen.root['dev']['qa1']['webapp']


def test_confgen_tree_leafs(confgen):
    assert set([i.path for i in confgen.root.services]) == {
        'infra/prod/main/webapp',
        'infra/prod/multiapp/webapp',
        'infra/prod/multiapp/api',
        'infra/prod/staging/webapp',
        'infra/prod/staging/api',
        'infra/dev/qa1/webapp',
        'infra/dev/qa1/api',
        'infra/dev/qa2/webapp',
        'infra/dev/qa2/api',
    }

def test_confgen_build(confgen):
    confgen.build()
    f = lambda p: open(join(confgen.home, confgen.build_dir, p)).read()
    assert f('prod/main/webapp/my.cnf') == "infra prod main webapp"
    assert f('prod/main/webapp/production.ini') == "3.0 password main multiapp staging"
    assert f('prod/multiapp/webapp/my.cnf') == "infra prod multiapp webapp"
    assert f('prod/multiapp/webapp/production.ini') == "2.0 password main multiapp staging"
    assert f('prod/multiapp/api/my.cnf') == "infra prod multiapp api"
    assert f('prod/staging/webapp/my.cnf') == "infra prod staging webapp"
    assert f('prod/staging/webapp/production.ini') == "2.0 password main multiapp staging"
    assert f('prod/staging/api/my.cnf') == "infra prod staging api"
    assert f('dev/qa1/webapp/my.cnf') == "infra dev qa1 webapp"
    assert f('dev/qa1/webapp/production.ini') == "4.0 password qa1 qa2"
    assert f('dev/qa1/api/my.cnf') == "infra dev qa1 api"
    assert f('dev/qa2/webapp/my.cnf') == "infra dev qa2 webapp"
    assert f('dev/qa2/webapp/production.ini') == "9.0 password qa1 qa2"
    assert f('dev/qa2/api/my.cnf') == "infra dev qa2 api"
