from __future__ import with_statement

from fabric.api import run, cd, prefix

from journeyman.buildrunner.registry import registry

def run_commands(build_runner, **kwargs):
    with cd(build_runner.build_src):
        with prefix('source ../bin/activate'):
            for command in kwargs.get('lines', []):
                output = run(command)
                if output.return_code != 0 and not kwargs.get('allow_fail', False):
                    return False, output.return_code
    return True, 0

registry.add_step('run_commands', run_commands)