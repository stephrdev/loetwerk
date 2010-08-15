import yaml, tempfile

from fabric.api import run, cd, get
from fabric.contrib.files import exists

from journeyman.buildrunner.registry import registry

class InvalidConfigFileException(Exception):
    pass

class InvalidConfigException(Exception):
    pass

def fetch_config(build_runner, **kwargs):
    if build_runner.build.project.config_file:
        with cd(build_runner.build_src):
            if not exists(build_runner.build.project.config_file):
                raise InvalidConfigFileException(
                    'Journey.conf not found: %s' % 
                        build_runner.build.project.config_file)

            pwd = run('pwd')
            config_file = tempfile.NamedTemporaryFile()
            get('%s/%s' % (pwd, build_runner.build.project.config_file),
                config_file.name)

            try:
                build_runner.config = yaml.load(config_file)
            except Exception, ex:
                raise InvalidConfigException(ex.message)
            finally:
                config_file.close()
    else:
        try:
            build_runner.config = yaml.load(
                build_runner.build.project.config_data)
        except Exception, ex:
            raise InvalidConfigException(ex.message)

    if 'options' not in build_runner.config:
        build_runner.config['options'] = {}
    if 'dependencies' in build_runner.config:
        raise InvalidConfigException(
            'build step dependencies is reserved')

    if 'build' not in build_runner.config:
        build_runner.config['build'] = ['dependencies', 'install', 'test',
            'testresults']

    if not set(build_runner.config['build']).issubset(
        set(build_runner.config.keys() + ['dependencies', 'testresults'])):
        raise InvalidConfigException(
            'some build steps are not configured')

    return True, 0

registry.add_step('fetch_config', fetch_config)