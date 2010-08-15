# We need this because the production environment runs python2.5
from __future__ import with_statement

import tempfile
from fabric.api import run, cd, get
from fabric.contrib.files import exists

from journeyman.buildrunner.registry import registry

def fetch_xunit_results(build_runner, **kwargs):
    with cd(build_runner.build_src):
        # Fetch the current directory.
        pwd = run('pwd')
        # Get all result xml files.
        files = kwargs.get('lines', [])
        for test_file in files:
            # Test if the result file exists.
            if exists(test_file):
                # Create a temp. file to download the xml
                local_test_file = tempfile.NamedTemporaryFile()
                # Loading...
                get('%s/%s' % (pwd, test_file),
                    local_test_file.name)

                # Store the plain xml data to database.
                build_runner.build.buildresult_set.create(
                    name=test_file,
                    body=''.join(local_test_file.readlines())
                )

                # Close the temp file.
                local_test_file.close()
    # Return.
    return True, 0

# Register the plugin
registry.add_step('fetch_xunit_results', fetch_xunit_results)
