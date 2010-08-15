# We need this because the production environment runs python2.5
from __future__ import with_statement

from fabric.api import run, cd

from journeyman.buildrunner.registry import registry

def fetch_repository_commit_id(build_runner, **kwargs):
    # FIXME: support multiple vcs types
    if not build_runner.build.project.repository.startswith('git+'):
        raise InvalidRepositoryException(
            'Invalid repository: %s' % build_runner.build.project.repository)

    # Move to the repo directory
    with cd(build_runner.build_src):
        # get the revision id and store in build runner instance
        output = run('git log --pretty="format:%H" -n 1')
        build_runner.repo_head_id = output
        output = run('git log --pretty="format:%h" -n 1')
        build_runner.repo_head_short_id = output

    # Pass the exit code of vcs.
    return output.return_code == 0, output.return_code

# Register the plugin
registry.add_step('fetch_repository_commit_id', fetch_repository_commit_id)