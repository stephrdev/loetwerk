from fabric.api import run, cd

from journeyman.buildrunner.registry import registry

def fetch_dependencies(build_runner, **kwargs):
    if 'pip-dependencies' in build_runner.config['options']:
        with cd(build_runner.build_src):
            files = build_runner.config['options']['pip-dependencies'].split(' ')
            for req_file in files:
                output = run('pip -E .. install -r %s' % req_file)
                if output.return_code != 0:
                    return False, output.return_code
    return True, 0

registry.add_step('fetch_dependencies', fetch_dependencies)