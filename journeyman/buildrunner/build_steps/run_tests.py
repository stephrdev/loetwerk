from __future__ import with_statement

from fabric.api import run, cd, prefix

from journeyman.buildrunner.registry import registry

def run_tests(build_runner, **kwargs):
    with cd(build_runner.build_src):
        with prefix('source ../bin/activate'):
            for command in kwargs.get('lines', []):
                output = run(command)
    return True, 0

registry.add_step('run_tests', run_tests)