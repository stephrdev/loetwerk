from StringIO import StringIO
import tempfile, yaml, sys
from journeyman.builds.models import Build, BUILD_STATES
from fabric.state import env
from fabric.api import run, cd, prefix, get
from fabric.contrib.files import exists
from fabric.main import update_output_levels
from fabric.network import disconnect_all
from django.utils import simplejson as json
from datetime import datetime

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
    repo_head_id = None

    def __init__(self, build):
        if type(build) == int:
            try:
                self.build = Build.objects.get(pk=build)
            except Build.DoesNotExist:
                raise InvalidBuildException('Invalid build id.')
        else:
            self.build = build

    def run_step(self, name, task, *args, **kwargs):
        step_starttime = datetime.now()
        stdout = StringIO()
        stderr = StringIO()
        sys.stdout = stdout
        sys.stderr = stderr
        try:
            output, return_code = task(*args, **kwargs)
            result = (True, None)
        except (SystemExit, Exception), e:
            output, return_code = '', 1
            result = (False, ('%s: %s' % (e.__class__.__name__, e.message)))
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        self.build.buildstep_set.create(
            name=name,
            successful=result[0],
            started=step_starttime,
            finished=datetime.now(),
            extra = json.dumps({
                'return_code': return_code,
                'exception_message': result[1],
                'stdout': stdout.getvalue(),
                'stderr': stderr.getvalue(),
                'output': output,
            }),
        )
        return result[0]

    def prepare_fabric(self):
        self.worker_ssh_key = tempfile.NamedTemporaryFile()
        self.worker_ssh_key.write(self.build.node.ssh_key)
        self.worker_ssh_key.flush()

        env.warn_only = True
        env.key_filename = self.worker_ssh_key.name
        env.user = self.build.node.username
        env.all_hosts = [self.build.node.host,]
        env.host_string = self.build.node.host

        return True, 0

    def prepare_ve(self):
        self.build_ve_name = 'journeyman.%s' % tempfile.mktemp(dir='')
        self.build_ve_path = 'builds/%s' % self.build_ve_name

        output = run('virtualenv %s' % self.build_ve_path)
        return output.return_code == 0, output.return_code

    def get_repository(self):
        # FIXME: support multiple vcs types
        if not self.build.project.repository.startswith('git+'):
            raise InvalidRepositoryException(
                'Invalid repository: %s' % self.build.project.repository)

        self.build_src = '%s/src' % self.build_ve_path

        output = run('git clone %s %s' % (
            ''.join(self.build.project.repository.split('+')[1:]),
            self.build_src))

        return output.return_code == 0, output.return_code

    def get_repo_head_id(self):
        # FIXME: support multiple vcs types
        if not self.build.project.repository.startswith('git+'):
            raise InvalidRepositoryException(
                'Invalid repository: %s' % self.build.project.repository)

        self.build_src = '%s/src' % self.build_ve_path
        with cd(self.build_src):
            output = run('git log --pretty="format:%H" -n 1')
            self.repo_head_id = output

        return output.return_code == 0, output.return_code

    def get_config(self):
        with cd(self.build_src):
            if not exists(self.build.project.config_file):
                raise InvalidConfigDirectoryException(
                    'Journey.conf not found: %s' % self.build.project.config_file)

            pwd = run('pwd')
            config_file = tempfile.NamedTemporaryFile()
            get('%s/%s' % (pwd, self.build.project.config_file),
                config_file.name)

            try:
                self.config = yaml.load(config_file)
            except Exception, e:
                raise InvalidConfigException(e.message)
            finally:
                config_file.close()

            if 'options' not in self.config:
                self.config['options'] = {}
            if 'dependencies' in self.config:
                raise InvalidConfigException('build step dependencies is reserved')

            if 'build' not in self.config:
                self.config['build'] = ['dependencies', 'install', 'test',]

            if not set(self.config['build']).issubset(set(self.config.keys() + ['dependencies',])):
                raise InvalidConfigException('some build steps are not configured')

        return True, 0

    def get_dependencies(self):
        if 'pip-dependencies' in self.config['options']:
            with cd(self.build_src):
                for req_file in self.config['options']['pip-dependencies'].split(' '):
                    output = run('pip -E .. install -r %s' % req_file)
                    if output.return_code <> 0:
                        return False, output.return_code
        return True, 0

    def get_results(self):
        if 'unittest-xml-results' not in self.config['options']:
            return True, 0

        with cd(self.build_src):
            pwd = run('pwd')
            for test_file in self.config['options']['unittest-xml-results'].split(' '):
                print test_file, exists(test_file)
                if exists(test_file):
                    local_test_file = tempfile.NamedTemporaryFile()
                    get('%s/%s' % (pwd, test_file),
                        local_test_file.name)
                    self.build.buildresult_set.create(
                        name=test_file,
                        body=''.join(local_test_file.readlines())
                    )
                    local_test_file.close()

        return True, 0

    def run_commands(self, commands, allow_fail=False):
        with cd(self.build_src):
            with prefix('source ../bin/activate'):
                for command in commands:
                    output = run(command)
                    if output.return_code <> 0 and not allow_fail:
                        return False, output.return_code
        return True, 0

    def run_build(self):
        self.build.started = datetime.now()
        self.build.state = BUILD_STATES.RUNNING
        self.build.save()
        result, state = self.run_build_steps()
        self.build.state = state
        self.build.revision = self.repo_head_id
        self.build.finished = datetime.now()
        self.build.save()

    def run_build_steps(self):
        try:
            if not self.run_step('prepare fabric', self.prepare_fabric):
                return False, BUILD_STATES.FAILED
            if not self.run_step('prepare virtualenv', self.prepare_ve):
                return False, BUILD_STATES.FAILED
            if not self.run_step('fetch repository', self.get_repository):
                return False, BUILD_STATES.FAILED
            if not self.run_step('fetch repo head id', self.get_repo_head_id):
                return False, BUILD_STATES.FAILED
            if not self.run_step('fetch config', self.get_config):
                return False, BUILD_STATES.FAILED

            for step in self.config['build']:
                if step == 'dependencies':
                    if not self.run_step('fetch dependencies', self.get_dependencies):
                        return False, BUILD_STATES.FAILED
                else:
                    if not self.run_step('execute %s' % step,
                        self.run_commands, self.config[step], step == 'test'):
                        return False, BUILD_STATES.FAILED

            if 'unittest-xml-results' in self.config['options']:
                if not self.run_step('fetch results', self.get_results):
                    return False, BUILD_STATES.FAILED
            return True, BUILD_STATES.STABLE
        finally:
            disconnect_all()
