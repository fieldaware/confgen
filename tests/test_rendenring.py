def test_collect_templates(renderer):
    assert renderer.templates == {
        'api': ['api/my.cnf'],
        'webapp': ['webapp/my.cnf', 'webapp/production.ini']
    }

def test_render_templates_for_given_service_and_inventory(renderer, inventory):
    built_inventory = inventory.build()

    templates = renderer.render_templates('webapp', built_inventory['/prod/main'])

    assert templates == {
        'webapp/my.cnf': u'connurl = 3.0:password',
        'webapp/production.ini': u'mysql = 3.0\npassword = password'
    }

    templates = renderer.render_templates('webapp', built_inventory['/dev/qa1'])

    assert templates == {
        'webapp/my.cnf': u'connurl = 4.0:password',
        'webapp/production.ini': u'mysql = 4.0\npassword = password'
    }

    templates = renderer.render_templates('api', built_inventory['/test'])

    assert templates == {
        'api/my.cnf': u'connurl = 1.0:plaintext',
    }

def test_render_templates_for_multiple_service_and_inventory(renderer, inventory):
    built_inventory = inventory.build()

    templates = renderer.render_multiple_templates(
        ['webapp', 'api'],
        built_inventory['/prod/main']
    )

    assert templates == {
        'webapp/my.cnf': u'connurl = 3.0:password',
        'webapp/production.ini': u'mysql = 3.0\npassword = password',
        'api/my.cnf': u'connurl = 3.0:password'
    }
