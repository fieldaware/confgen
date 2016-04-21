import os
import tempfile

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

def test_collecting_inventory_plus_temaples(confgen):
    assert confgen.collect() == {
        '/dev/qa1/webapp/my.cnf': u'connurl = 4.0:password',
        '/dev/qa1/webapp/production.ini': u'mysql = 4.0\npassword = password',
        '/dev/qa1/api/my.cnf': u'connurl = 4.0:password',
        '/prod/main/api1/api/my.cnf': u'connurl = 3.0:password',
        '/prod/main/multiapp/webapp/my.cnf': u'connurl = 3.0:password',
        '/prod/main/multiapp/webapp/production.ini': u'mysql = 3.0\npassword = password',
        '/prod/main/multiapp/api/my.cnf': u'connurl = 3.0:password',
        '/prod/main/webapp1/webapp/my.cnf': u'connurl = 3.0:password',
        '/prod/main/webapp1/webapp/production.ini': u'mysql = 3.0\npassword = password',
        '/prod/staging/webapp/my.cnf': u'connurl = 2.0:password',
        '/prod/staging/webapp/production.ini': u'mysql = 2.0\npassword = password',
        '/prod/staging/api/my.cnf': u'connurl = 2.0:password',
        '/test/webapp/my.cnf': u'connurl = 1.0:plaintext',
        '/test/webapp/production.ini': u'mysql = 1.0\npassword = plaintext',
        '/test/api/my.cnf': u'connurl = 1.0:plaintext',
        '/demo/webapp/my.cnf': u'connurl = 1.0:password',
        '/demo/webapp/production.ini': u'mysql = 1.0\npassword = password',
    }


def test_flush_path_exists(confgen):
    rootdir = tempfile.mkdtemp()
    confgen.home = rootdir
    os.makedirs(os.path.join(rootdir, confgen.build_dir, 'webapp'))
    collected = {
        '/webapp/production.ini': "FILE_CONTENTS"
    }
    confgen.flush(collected)
    assert open(os.path.join(rootdir, confgen.build_dir, 'webapp/production.ini')).read() == "FILE_CONTENTS"

def test_flush_path_doesnt_exist(confgen):
    rootdir = tempfile.mkdtemp()
    confgen.home = rootdir
    collected = {
        '/long/complex/path/webapp/production.ini': "FILE_CONTENTS"
    }
    confgen.flush(collected)
    assert open(os.path.join(rootdir, confgen.build_dir, 'long/complex/path/webapp/production.ini')).read() == "FILE_CONTENTS"


def test_flush_multiple_files(confgen):
    rootdir = tempfile.mkdtemp()
    confgen.home = rootdir
    collected = {
        '/prod/main/multiapp/webapp/my.cnf': "FILE_CONTENTS",
        '/prod/main/multiapp/webapp/production.ini': "FILE_CONTENTS",
        '/prod/main/multiapp/api/my.cnf': "FILE_CONTENTS",
        '/prod/main/webapp1/webapp/my.cnf': "FILE_CONTENTS",
        '/prod/main/webapp1/webapp/production.ini': "FILE_CONTENTS",
        '/prod/staging/webapp/my.cnf': "FILE_CONTENTS",
        '/prod/staging/webapp/production.ini': "FILE_CONTENTS",
        '/prod/staging/api/my.cnf': "FILE_CONTENTS",
        '/test/webapp/my.cnf': "FILE_CONTENTS",
        '/test/webapp/production.ini': "FILE_CONTENTS",
    }
    confgen.flush(collected)

    j = lambda x: os.path.join(rootdir, confgen.build_dir, x)
    assert open(j('prod/main/multiapp/webapp/my.cnf')).read() == "FILE_CONTENTS"
    assert open(j('prod/main/multiapp/webapp/production.ini')).read() == "FILE_CONTENTS"
    assert open(j('prod/main/multiapp/api/my.cnf')).read() == "FILE_CONTENTS"
    assert open(j('prod/main/webapp1/webapp/my.cnf')).read() == "FILE_CONTENTS"
    assert open(j('prod/main/webapp1/webapp/production.ini')).read() == "FILE_CONTENTS"
    assert open(j('prod/staging/webapp/my.cnf')).read() == "FILE_CONTENTS"
    assert open(j('prod/staging/webapp/production.ini')).read() == "FILE_CONTENTS"
    assert open(j('prod/staging/api/my.cnf')).read() == "FILE_CONTENTS"
    assert open(j('test/webapp/my.cnf')).read() == "FILE_CONTENTS"
    assert open(j('test/webapp/production.ini')).read() == "FILE_CONTENTS"
