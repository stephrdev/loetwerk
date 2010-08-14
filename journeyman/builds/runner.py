import tempfile, yaml
from journeyman.builds.models import Build
from fabric.state import env
from fabric.api import run, cd, prefix, get
from fabric.contrib.files import exists
from django.utils import simplejson as json

class InvalidBuildException(Exception): pass
class InvalidRepositoryException(Exception): pass
class InvalidConfigDirectoryException(Exception): pass
class InvalidConfigException(Exception): pass

class BuildRunner(object):
    build = None
    worker_ssh_key = None
    build_ve_name = None
    build_ve_path = None
    build_src = None

    def __init__(self, build):
        if type(build) == int:
            try:
                self.build = Build.objects.get(pk=build)
            except Build.DoesNotExist:
                raise InvalidBuildException('Invalid build id.')
        else:
            self.build = build

    def prepare_fabric(self):
        self.worker_ssh_key = tempfile.NamedTemporaryFile()
        self.worker_ssh_key.write(self.build.node.ssh_key)
        self.worker_ssh_key.flush()

        env.key_filename = self.worker_ssh_key.name
        env.user = self.build.node.username
        env.all_hosts = [self.build.node.host,]
        env.host_string = self.build.node.host

    def prepare_ve(self):
        self.build_ve_name = 'journeyman.%s' % tempfile.mktemp(dir='')
        self.build_ve_path = 'builds/%s' % self.build_ve_name
        run('virtualenv %s' % self.build_ve_path)

    def get_repository(self):
        # FIXME: support multiple vcs types
        if not self.build.project.repository.startswith('git+'):
            raise InvalidRepositoryException('Invalid repository: %s' % self.build.project.repository)

        self.build_src = '%s/src' % self.build_ve_path
        run('git clone %s %s' % (self.build.project.repository, self.build_src))

    def get_config(self):
        with cd(self.build_src):
            remote_config_file = '%s/config' % self.build.project.config_dir
            if not exists(remote_config_file):
                raise InvalidConfigDirectoryException('Journey.conf not found: %s' % self.build.project.config_dir)

            pwd = run('pwd')
            config_file = tempfile.NamedTemporaryFile()
            get('%s/' % (pwd, remote_config_file), config_file.name)
            try:
                self.config = yaml.load(config_file)
            except Exception, e:
                raise InvalidConfigException(e.message)
            finally:
                config_file.close()

    def run_build(self):
        self.build.buildstep_set.create(
            name='prepare fabric',
            successful=True,
            extra = json.dumps({'out': 'ok'}),
        )
