import pytest

@pytest.mark.parametrize("path, expected", (
    (
        'infra/prod/main/webapp', {
            'my.cnf': u"infra prod main webapp",
            'production.ini': u"3.0 password main multiapp staging"
        }
    ),
    (
        'infra/prod/multiapp/api', {
            'my.cnf': u"infra prod multiapp api",
        }
    ),
    (
        'infra/dev/qa1/webapp', {
            'my.cnf': u"infra dev qa1 webapp",
            'production.ini': u"4.0 password qa1 qa2"
        }
    ),
    (
        'infra/dev/qa2/api', {
            'my.cnf': u"infra dev qa2 api",
        }
    ),

))
def test_render_service(confgen, renderer, path, expected):
    assert renderer.service(confgen.root.by_path(path)) == expected
