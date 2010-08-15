# We need this because the production environment runs python2.5
from __future__ import with_statement

import tempfile
from fabric.api import run

from journeyman.buildrunner.registry import registry

def prepare_virtualenv(build_runner, **kwargs):
    # Prepare some paths.
    build_runner.build_ve_name = 'journeyman.%s' % tempfile.mktemp(dir='')
    build_runner.build_ve_path = 'builds/%s' % build_runner.build_ve_name

    # Create the virtual env for testing.
    output = run('virtualenv %s' % build_runner.build_ve_path)

    # Return the exit code of virtualenv.
    return output.return_code == 0, output.return_code

# Register the plugin
registry.add_step('prepare_virtualenv', prepare_virtualenv)