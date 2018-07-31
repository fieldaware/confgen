import pytest


@pytest.mark.parametrize("path, expected", (
    (
        '/prod/main/webapp', {
            'my.cnf': u"/ prod main webapp",
            'production.ini': u"3.0 password main multiapp staging"
        }
    ),
    (
        '/prod/multiapp/api', {
            'my.cnf': u"/ prod multiapp api",
        }
    ),
    (
        '/dev/qa1/webapp', {
            'my.cnf': u"/ dev qa1 webapp",
            'production.ini': u"4.0 password qa1 qa2"
        }
    ),
    (
        '/dev/qa2/api', {
            'my.cnf': u"/ dev qa2 api",
        }
    ),

))
def test_render_service(confgen, renderer, path, expected):
    assert renderer.service(confgen.root.by_path(path)) == expected


@pytest.mark.parametrize("path, expected", (
    (
        '/prod/main', {
            'my.cnf': u"/ prod main",
            'production.ini': u"3.0 password main multiapp staging"
        }
    ),
    (
        '/prod/multiapp', {
            'my.cnf': u"/ prod multiapp",
            'production.ini': u'2.0 password main multiapp staging'
        }
    ),
    (
        '/dev/qa1', {
            'my.cnf': u"/ dev qa1",
            'production.ini': u"4.0 password qa1 qa2"
        }
    ),
    (
        '/dev/qa2', {
            'my.cnf': u"/ dev qa2",
            'production.ini': u"9.0 password qa1 qa2"
        }
    ),

))
def test_render_service(confgen_single_service, renderer_singleservice, path, expected):
    confgen = confgen_single_service
    renderer = renderer_singleservice
    assert renderer.service(confgen.root.by_path(path), anon_service=True) == expected
