import sys, tempfile, traceback
from StringIO import StringIO
from datetime import datetime

from fabric.state import env
from fabric.network import disconnect_all

from django.utils import simplejson as json

from journeyman.builds.models import Build, BuildState
from journeyman.buildrunner.registry import registry, StepNotFound

class InvalidBuildException(Exception):
    pass

class BuildRunner(object):
    worker_ssh_key = None
    config = None

    build = None
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

        self.worker_ssh_key = tempfile.NamedTemporaryFile()
        self.worker_ssh_key.write(self.build.node.ssh_key)
        self.worker_ssh_key.flush()

        env.warn_only = True
        env.key_filename = self.worker_ssh_key.name
        env.user = self.build.node.username
        env.all_hosts = [self.build.node.host,]
        env.host_string = self.build.node.host

    def run_build(self):
        self.build.started = datetime.now()
        self.build.state = BuildState.RUNNING
        self.build.save()

        result = self.run_all_steps()

        self.build.state = BuildState.STABLE
        for build_result in self.build.buildresult_set.all():
            if build_result.buildstate != BuildState.STABLE:
                self.build.state = build_result.buildstate

        self.build.revision = self.repo_head_id
        self.build.finished = datetime.now()
        self.build.save()

    def run_all_steps(self):
        def _execute_steps(steps):
            for step in steps:
                try:
                    if len(step) == 3:
                        if not self.run_step(step[0], step[1](), **step[2]):
                            return False
                    else:
                        if not self.run_step(step[0], step[1]()):
                            return False
                except StepNotFound, ex:
                    self.build.buildstep_set.create(
                        name=step[0],
                        successful=False,
                        started=datetime.now(),
                        finished=datetime.now(),
                        extra = json.dumps({
                            'return_code': 1,
                            'exception_message': ex.message,
                        }),
                    )
                    return False
            return True

        try:
            steps = [
                ('prepare virtualenv',
                    registry.get_step('prepare_virtualenv')),
                ('fetch repository',
                    registry.get_step('fetch_repository')),
                ('fetch commit id',
                    registry.get_step('fetch_repository_commit_id')),
                ('fetch config',
                    registry.get_step('fetch_config'))
            ]
            result = _execute_steps(steps)
            if not result:
                return result

            steps = []

            for step in self.config['build']:
                plugin = step.split('[')[1][:-1] if len(step.split('[')) == 2 else 'run_commands'

                steps.append(('execute step %s (%s)' % (step.split('[')[0], plugin),
                    registry.get_step(plugin), {
                        'lines': self.config[step],
                    }))

            result = _execute_steps(steps)
            if not result:
                return result

        finally:
            disconnect_all()

        return True

    def run_step(self, name, task, **kwargs):
        step_starttime = datetime.now()
        stdout = StringIO()
        stderr = StringIO()
        sys.stdout = stdout
        sys.stderr = stderr
        try:
            output, return_code = task(self, **kwargs)
            result = (output, None)
        except (SystemExit, Exception), ex:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            exc =  "".join(traceback.format_tb(exceptionTraceback))
            exc += " ".join((str(exceptionType), str(exceptionValue)))
            
            output, return_code = '', 1
            result = (False, exc)
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
