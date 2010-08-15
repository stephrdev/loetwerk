import tempfile
from fabric.api import run, cd, get
from fabric.contrib.files import exists

from journeyman.buildrunner.registry import registry

def fetch_xunit_results(build_runner, **kwargs):
    if 'unittest-xml-results' not in build_runner.config['options']:
        return True, 0

    with cd(build_runner.build_src):
        pwd = run('pwd')
        files = build_runner.config['options']['unittest-xml-results'].split(' ')
        for test_file in files:
            if exists(test_file):
                local_test_file = tempfile.NamedTemporaryFile()
                get('%s/%s' % (pwd, test_file),
                    local_test_file.name)
                build_runner.build.buildresult_set.create(
                    name=test_file,
                    body=''.join(local_test_file.readlines())
                )
                local_test_file.close()

    return True, 0

registry.add_step('fetch_xunit_results', fetch_xunit_results)
