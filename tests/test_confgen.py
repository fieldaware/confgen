def test_merge_config_with_inventory(confgen):
    built_config = confgen.merge_config_with_inventory()
    assert built_config == {
        '/dev/qa1': {'mysql': 4.0, 'secret': 'password'},
        '/prod/main/api1': {'mysql': 3.0, 'secret': 'password'},
        '/prod/main/multiapp': {'mysql': 3.0, 'secret': 'password'},
        '/prod/main/webapp1': {'mysql': 3.0, 'secret': 'password'},
        '/prod/staging': {'mysql': 2.0, 'secret': 'password'},
        '/test': {'mysql': 1.0, 'secret': 'plaintext'},
        '/demo': {'mysql': 1.0, 'secret': 'password'},
    }

def test_build(confgen):
    assert confgen.build() == {
        '/dev/qa1': {
            'webapp/my.cnf': u'connurl = 4.0:password',
            'webapp/production.ini': u'mysql = 4.0\npassword = password',
            'api/my.cnf': u'connurl = 4.0:password',
        },
        '/prod/main/api1': {
            'api/my.cnf': u'connurl = 3.0:password',
        },
        '/prod/main/multiapp': {
            'webapp/my.cnf': u'connurl = 3.0:password',
            'webapp/production.ini': u'mysql = 3.0\npassword = password',
            'api/my.cnf': u'connurl = 3.0:password',
        },
        '/prod/main/webapp1': {
            'webapp/my.cnf': u'connurl = 3.0:password',
            'webapp/production.ini': u'mysql = 3.0\npassword = password',
        },
        '/prod/staging': {
            'webapp/my.cnf': u'connurl = 2.0:password',
            'webapp/production.ini': u'mysql = 2.0\npassword = password',
            'api/my.cnf': u'connurl = 2.0:password',
        },
        '/test': {
            'webapp/my.cnf': u'connurl = 1.0:plaintext',
            'webapp/production.ini': u'mysql = 1.0\npassword = plaintext',
            'api/my.cnf': u'connurl = 1.0:plaintext',
        },
        '/demo': {
            'webapp/my.cnf': u'connurl = 1.0:password',
            'webapp/production.ini': u'mysql = 1.0\npassword = password',
        },
    }
