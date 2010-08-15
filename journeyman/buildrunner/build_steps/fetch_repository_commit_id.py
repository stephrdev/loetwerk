from fabric.api import run, cd

from journeyman.buildrunner.registry import registry

def fetch_repository_commit_id(build_runner, **kwargs):
    # FIXME: support multiple vcs types
    if not build_runner.build.project.repository.startswith('git+'):
        raise InvalidRepositoryException(
            'Invalid repository: %s' % build_runner.build.project.repository)

    build_runner.build_src = '%s/src' % build_runner.build_ve_path
    with cd(build_runner.build_src):
        output = run('git log --pretty="format:%H" -n 1')
        build_runner.repo_head_id = output

    return output.return_code == 0, output.return_code

registry.add_step('fetch_repository_commit_id', fetch_repository_commit_id)