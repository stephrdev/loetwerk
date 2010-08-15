# We need this because the production environment runs python2.5
from __future__ import with_statement

from fabric.api import run, cd

from journeyman.buildrunner.registry import registry

def fetch_pip_dependencies(build_runner, **kwargs):
    # Move into the source/repo directory
    with cd(build_runner.build_src):
        # Get files from config
        files = kwargs.get('lines', [])
        for req_file in files:
            # do the pip install dance for every requirements file
            output = run('pip -E .. install -r %s' % req_file)
            # if anything else than 0 returned, abort.
            if output.return_code != 0:
                return False, output.return_code

    # Done!
    return True, 0

# Register the plugin
registry.add_step('fetch_pip_dependencies', fetch_pip_dependencies)