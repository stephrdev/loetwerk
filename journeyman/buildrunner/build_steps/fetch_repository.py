# We need this because the production environment runs python2.5
from __future__ import with_statement

from fabric.api import run

from journeyman.buildrunner.registry import registry

class InvalidRepositoryException(Exception):
    pass

def fetch_repository(build_runner, **kwargs):
    # FIXME: support multiple vcs types
    if not build_runner.build.project.repository.startswith('git+'):
        raise InvalidRepositoryException(
            'Invalid repository: %s' % build_runner.build.project.repository)

    # Generate the repo path.
    build_runner.build_src = '%s/src' % build_runner.build_ve_path

    # Execute the clone command.
    output = run('git clone %s %s' % (
        ''.join(build_runner.build.project.repository.split('+')[1:]),
        build_runner.build_src))

    # Pass the return code of the vcs.
    return output.return_code == 0, output.return_code

# Register the plugin
registry.add_step('fetch_repository', fetch_repository)