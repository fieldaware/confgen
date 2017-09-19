import pytest

def test_collect_templates(renderer):
    assert renderer.collect_templates_for_services(renderer.services) == {
        'api': ['api/my.cnf'],
        'webapp': ['webapp/my.cnf', 'webapp/production.ini']
    }

def test_render_templates_for_given_service_and_inventory(renderer, confgen):
    built_inventory = confgen.merge_config_with_inventory()

    templates = renderer.render_templates_for_service('webapp', built_inventory['/prod/main/webapp1'])

    assert templates == {
        'webapp/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        'webapp/production.ini': u'# mysql:/ override: /prod, /prod/main\nmysql = 3.0\n\n# secret:/\npassword = password',
    }

    templates = renderer.render_templates_for_service('webapp', built_inventory['/dev/qa1'])

    assert templates == {
        'webapp/my.cnf': u'# mysql:/ override: /dev/qa1\n# secret:/\nconnurl = 4.0:password',
        'webapp/production.ini': u'# mysql:/ override: /dev/qa1\nmysql = 4.0\n\n# secret:/\npassword = password',
    }

    templates = renderer.render_templates_for_service('api', built_inventory['/test'])

    assert templates == {
        'api/my.cnf': u'# mysql:/\n# secret:/ override: /test\nconnurl = 1.0:plaintext',
    }

def test_render_templates_for_multiple_service_and_inventory(renderer, confgen):
    built_inventory = confgen.merge_config_with_inventory()

    templates = renderer.render_templates_for_services(
        ['webapp', 'api'],
        built_inventory['/prod/main/webapp1']
    )

    assert templates == {
        'api/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        'webapp/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        'webapp/production.ini': u'# mysql:/ override: /prod, /prod/main\nmysql = 3.0\n\n# secret:/\npassword = password',
    }

def test_render_template_with_undefined_key(renderer, confgen):
    built_inventory = confgen.merge_config_with_inventory()

    built_inventory['/prod/main/webapp1'].data.pop('secret')  # remove required key to render

    with pytest.raises(SystemExit):
        renderer.render_templates_for_service('webapp', built_inventory['/prod/main/webapp1'])
