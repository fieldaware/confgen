import confgen
from confgen import cli

def test_version(runner):
    cmd = runner.invoke(cli.version)
    assert cmd.output.strip() == confgen.__version__
    assert cmd.exit_code == 0
