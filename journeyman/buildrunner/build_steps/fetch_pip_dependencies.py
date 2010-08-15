from fabric.api import run, cd

from journeyman.buildrunner.registry import registry

def fetch_pip_dependencies(build_runner, **kwargs):
    with cd(build_runner.build_src):
        files = kwargs.get('lines', [])
        for req_file in files:
            output = run('pip -E .. install -r %s' % req_file)
            if output.return_code != 0:
                return False, output.return_code
    return True, 0

registry.add_step('fetch_pip_dependencies', fetch_pip_dependencies)