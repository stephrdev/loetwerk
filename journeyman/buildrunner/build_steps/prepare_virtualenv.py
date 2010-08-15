import tempfile
from fabric.api import run

from __future__ import with_statement

from journeyman.buildrunner.registry import registry

def prepare_virtualenv(build_runner, **kwargs):
    build_runner.build_ve_name = 'journeyman.%s' % tempfile.mktemp(dir='')
    build_runner.build_ve_path = 'builds/%s' % build_runner.build_ve_name

    output = run('virtualenv %s' % build_runner.build_ve_path)
    return output.return_code == 0, output.return_code

registry.add_step('prepare_virtualenv', prepare_virtualenv)