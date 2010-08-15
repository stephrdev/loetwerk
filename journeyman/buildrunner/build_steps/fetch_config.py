# We need this because the production environment runs python2.5
from __future__ import with_statement

import yaml, tempfile

from fabric.api import run, cd, get
from fabric.contrib.files import exists

from journeyman.buildrunner.registry import registry

class InvalidConfigFileException(Exception):
    pass

class InvalidConfigException(Exception):
    pass

def fetch_config(build_runner, **kwargs):
    # Check if we have a config file in the repository
    if build_runner.build.project.config_file:
        # Move to the directory
        with cd(build_runner.build_src):
            # Check if the file really exists.
            if not exists(build_runner.build.project.config_file):
                # No file found, error!
                raise InvalidConfigFileException(
                    'Journey.conf not found: %s' % 
                        build_runner.build.project.config_file)

            # We need the current directory for the download
            pwd = run('pwd')
            # .. and a local file to temp. store the config
            config_file = tempfile.NamedTemporaryFile()
            # Download!
            get('%s/%s' % (pwd, build_runner.build.project.config_file),
                config_file.name)

            try:
                # Try to parse the config
                build_runner.config = yaml.load(config_file)
            except Exception, ex:
                # OK, there is a config but the config is broken.
                raise InvalidConfigException(ex.message)
            finally:
                # Close the temp. file
                config_file.close()
    else:
        # No config file in the repository, we use the stored config from
        # project settings.
        try:
            build_runner.config = yaml.load(
                build_runner.build.project.config_data)
        except Exception, ex:
            # The stored config is broken.
            raise InvalidConfigException(ex.message)

    # Check if build steps are configured, if not.. set a default list.
    if 'build' not in build_runner.config:
        build_runner.config['build'] = [
            'dependencies',
            'install',
            'test',
            'testresults'
        ]
        build_runner.config['build_plugins'] = {
            'test': 'run_tests',
            'dependencies': 'fetch_pip_dependencies'
        }
    else:
        # Store plugins
        build_runner.config['build_plugins'] = dict(
            [(k.split('[')[0], k.split('[')[1][:-1]) \
            for k in build_runner.config.keys() if len(k.split('[')) == 2])

    # Maybe we need cleaned step names. Remove the plugin names.
    build_runner.config['build_names'] = [k.split('[')[0]
        for k in build_runner.config.keys()]

    # Check if we have commands/input for every step.
    if not set(build_runner.config['build']).issubset(
        set(build_runner.config['build_names'])):
        raise InvalidConfigException(
            'some build steps are not configured')

    # OK, we're done.
    return True, 0

# Register the plugin.
registry.add_step('fetch_config', fetch_config)