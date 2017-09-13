import os
import pytest
import tempfile

def test_merge_config_with_inventory(confgen):
    built_config = confgen.merge_config_with_inventory()
    assert built_config['/demo'].mysql == 1.0
    assert built_config['/demo'].mysql__source == '/'
    assert built_config['/demo'].secret == 'password'
    assert built_config['/demo'].secret__source == '/'
    assert built_config['/dev/qa1'].mysql == 4.0
    assert built_config['/dev/qa1'].mysql__source == '/ override: /dev/qa1'
    assert built_config['/dev/qa1'].secret == 'password'
    assert built_config['/dev/qa1'].secret__source == '/'
    assert built_config['/prod/main/api1'].mysql == 3.0
    assert built_config['/prod/main/api1'].mysql__source == '/ override: /prod, /prod/main'
    assert built_config['/prod/main/api1'].secret == 'password'
    assert built_config['/prod/main/api1'].secret__source == '/'
    assert built_config['/prod/main/multiapp'].mysql == 3.0
    assert built_config['/prod/main/multiapp'].mysql__source == '/ override: /prod, /prod/main'
    assert built_config['/prod/main/multiapp'].secret == 'password'
    assert built_config['/prod/main/multiapp'].secret__source == '/'
    assert built_config['/prod/main/webapp1'].mysql == 3.0
    assert built_config['/prod/main/webapp1'].mysql__source == '/ override: /prod, /prod/main'
    assert built_config['/prod/main/webapp1'].secret == 'password'
    assert built_config['/prod/main/webapp1'].secret__source == '/'
    assert built_config['/prod/staging'].mysql == 2.0
    assert built_config['/prod/staging'].mysql__source == '/ override: /prod'
    assert built_config['/prod/staging'].secret == 'password'
    assert built_config['/prod/staging'].secret__source == '/'
    assert built_config['/test'].mysql == 1.0
    assert built_config['/test'].mysql__source == '/'
    assert built_config['/test'].secret == 'plaintext'
    assert built_config['/test'].secret__source == '/ override: /test'

def test_collecting_inventory_plus_temaples(confgen):
    assert confgen.collect() == {
        '/demo/webapp/my.cnf': u'# mysql:/\n# secret:/\nconnurl = 1.0:password',
        '/demo/webapp/production.ini': u'# mysql:/\nmysql = 1.0\n\n# secret:/\npassword = password',
        '/dev/qa1/api/my.cnf': u'# mysql:/ override: /dev/qa1\n# secret:/\nconnurl = 4.0:password',
        '/dev/qa1/webapp/my.cnf': u'# mysql:/ override: /dev/qa1\n# secret:/\nconnurl = 4.0:password',
        '/dev/qa1/webapp/production.ini': u'# mysql:/ override: /dev/qa1\nmysql = 4.0\n\n# secret:/\npassword = password',
        '/prod/main/api1/api/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        '/prod/main/multiapp/api/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        '/prod/main/multiapp/webapp/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        '/prod/main/multiapp/webapp/production.ini': u'# mysql:/ override: /prod, /prod/main\nmysql = 3.0\n\n# secret:/\npassword = password',
        '/prod/main/webapp1/webapp/my.cnf': u'# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        '/prod/main/webapp1/webapp/production.ini': u'# mysql:/ override: /prod, /prod/main\nmysql = 3.0\n\n# secret:/\npassword = password',
        '/prod/staging/api/my.cnf': u'# mysql:/ override: /prod\n# secret:/\nconnurl = 2.0:password',
        '/prod/staging/webapp/my.cnf': u'# mysql:/ override: /prod\n# secret:/\nconnurl = 2.0:password',
        '/prod/staging/webapp/production.ini': u'# mysql:/ override: /prod\nmysql = 2.0\n\n# secret:/\npassword = password',
        '/test/api/my.cnf': u'# mysql:/\n# secret:/ override: /test\nconnurl = 1.0:plaintext',
        '/test/webapp/my.cnf': u'# mysql:/\n# secret:/ override: /test\nconnurl = 1.0:plaintext',
        '/test/webapp/production.ini': u'# mysql:/\nmysql = 1.0\n\n# secret:/ override: /test\npassword = plaintext'
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


def test_build(confgen):
    rootdir = tempfile.mkdtemp()
    confgen.home = rootdir

    confgen.build()

    build_files = {}
    for path, _, files in os.walk(os.path.join(confgen.home, confgen.build_dir)):
        if files:
            for f in files:
                f_path = os.path.join(path, f)
                build_files[f_path] = open(f_path).read()

    j = lambda x: os.path.join(rootdir, confgen.build_dir, x.strip('/'))
    assert build_files == {
        j('/demo/webapp/my.cnf'): '# mysql:/\n# secret:/\nconnurl = 1.0:password',
        j('/demo/webapp/production.ini'): '# mysql:/\nmysql = 1.0\n\n# secret:/\npassword = password',
        j('/dev/qa1/api/my.cnf'): '# mysql:/ override: /dev/qa1\n# secret:/\nconnurl = 4.0:password',
        j('/dev/qa1/webapp/my.cnf'): '# mysql:/ override: /dev/qa1\n# secret:/\nconnurl = 4.0:password',
        j('/dev/qa1/webapp/production.ini'): '# mysql:/ override: /dev/qa1\nmysql = 4.0\n\n# secret:/\npassword = password',
        j('/prod/main/api1/api/my.cnf'): '# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        j('/prod/main/multiapp/api/my.cnf'): '# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        j('/prod/main/multiapp/webapp/my.cnf'): '# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        j('/prod/main/multiapp/webapp/production.ini'): '# mysql:/ override: /prod, /prod/main\nmysql = 3.0\n\n# secret:/\npassword = password',
        j('/prod/main/webapp1/webapp/my.cnf'): '# mysql:/ override: /prod, /prod/main\n# secret:/\nconnurl = 3.0:password',
        j('/prod/main/webapp1/webapp/production.ini'): '# mysql:/ override: /prod, /prod/main\nmysql = 3.0\n\n# secret:/\npassword = password',
        j('/prod/staging/api/my.cnf'): '# mysql:/ override: /prod\n# secret:/\nconnurl = 2.0:password',
        j('/prod/staging/webapp/my.cnf'): '# mysql:/ override: /prod\n# secret:/\nconnurl = 2.0:password',
        j('/prod/staging/webapp/production.ini'): '# mysql:/ override: /prod\nmysql = 2.0\n\n# secret:/\npassword = password',
        j('/test/api/my.cnf'): '# mysql:/\n# secret:/ override: /test\nconnurl = 1.0:plaintext',
        j('/test/webapp/my.cnf'): '# mysql:/\n# secret:/ override: /test\nconnurl = 1.0:plaintext',
        j('/test/webapp/production.ini'): '# mysql:/\nmysql = 1.0\n\n# secret:/ override: /test\npassword = plaintext',
    }
