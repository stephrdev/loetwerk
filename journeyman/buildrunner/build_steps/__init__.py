# Import every plugin to get visible for the autodiscover method.
from journeyman.buildrunner.build_steps import fetch_config, \
    fetch_pip_dependencies, fetch_repository, fetch_repository_commit_id, \
    fetch_xunit_results, prepare_virtualenv, run_commands, run_tests
