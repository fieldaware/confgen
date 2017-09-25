import pytest

@pytest.mark.parametrize("path, expected", (
    (
        ('prod', 'main', 'webapp'), {
            'my.cnf': u"infra prod main webapp",
            'production.ini': u"3.0 password main multiapp staging"
        }
    ),
    (
        ('prod', 'multiapp', 'api'), {
            'my.cnf': u"infra prod multiapp api",
        }
    ),
    (
        ('dev', 'qa1', 'webapp'), {
            'my.cnf': u"infra dev qa1 webapp",
            'production.ini': u"4.0 password qa1 qa2"
        }
    ),
    (
        ('dev', 'qa2', 'api'), {
            'my.cnf': u"infra dev qa2 api",
        }
    ),

))
def test_render_service(confgen, renderer, path, expected):
    confgen.inventory.collect(confgen.root)
    assert renderer.service(confgen.root.by_path(path)) == expected
