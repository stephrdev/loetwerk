# We need this because the production environment runs python2.5
from __future__ import with_statement

from fabric.api import run, cd, prefix

from journeyman.buildrunner.registry import registry

def run_tests(build_runner, **kwargs):
    # Move to the repo directory
    with cd(build_runner.build_src):
        # Execute every command withing the virtualenv.
        with prefix('source ../bin/activate'):
            for command in kwargs.get('lines', []):
                # Execute the command. We ignore the results.
                output = run(command)

    # Its ok if errors occur.
    return True, 0

# Register the plugin
registry.add_step('run_tests', run_tests)