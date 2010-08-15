# We need this because the production environment runs python2.5
from __future__ import with_statement

import tempfile
from fabric.api import run

from journeyman.buildrunner.registry import registry

def teardown_virtualenv(build_runner, **kwargs):
    # Create the virtual env for testing.
    output = run('rm -rf %s' % build_runner.build_ve_path)

    # Return the exit code of virtualenv.
    return output.return_code == 0, output.return_code

# Register the plugin
registry.add_step('teardown_virtualenv', teardown_virtualenv)