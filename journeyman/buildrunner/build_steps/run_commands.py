# We need this because the production environment runs python2.5
from __future__ import with_statement

from fabric.api import run, cd, prefix

from journeyman.buildrunner.registry import registry

def run_commands(build_runner, **kwargs):
    # Move to the repo directory
    with cd(build_runner.build_src):
        # Every command should get executed within the virtualenv.
        with prefix('source ../bin/activate'):
            for command in kwargs.get('lines', []):
                #  Execute every command.
                output = run(command)

                # We assume that everything works, if not. Abort the step
                if output.return_code != 0:
                    return False, output.return_code

    # Done.
    return True, 0

# Register the plugin
registry.add_step('run_commands', run_commands)