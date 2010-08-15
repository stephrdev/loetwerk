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
    repo_head_short_id = None

    def __init__(self, build):
        # We accept Build objects and Build ids
        if type(build) == int:
            try:
                self.build = Build.objects.get(pk=build)
            except Build.DoesNotExist:
                raise InvalidBuildException('Invalid build id.')
        else:
            self.build = build

        # Fabric needs the ssh key for the worker as file, no stdin
        self.worker_ssh_key = tempfile.NamedTemporaryFile()
        self.worker_ssh_key.write(self.build.node.ssh_key)
        self.worker_ssh_key.flush()

        # Configure the Fabric environment
        env.warn_only = True
        env.key_filename = self.worker_ssh_key.name
        env.user = self.build.node.username
        env.all_hosts = [self.build.node.host,]
        env.host_string = self.build.node.host

    def run_build(self):
        # Maybe the last try failed, remove old results.
        self.build.buildstep_set.all().delete()
        self.build.buildresult_set.all().delete()

        # Set a timestamp when starting a build an change the build state
        self.build.started = datetime.now()
        self.build.state = BuildState.RUNNING

        # Save to allow website users to see the current state
        self.build.save()

        # Hand over control to the step runner
        result = self.run_all_steps()

        # Look for failed steps.
        if self.build.buildstep_set.filter(successful=False).count() > 0:
            self.build.state = BuildState.FAILED
        else:
            # Look for build results if all build steps where successful.
            for build_result in self.build.buildresult_set.all():
                if build_result.buildstate != BuildState.STABLE:
                    self.build.state = build_result.buildstate

        # Save the revision, we tested against and the finished timestamp.
        self.build.revision = self.repo_head_id
        self.build.short_revision = self.repo_head_short_id
        self.build.finished = datetime.now()
        self.build.save()

    def run_all_steps(self):
        # We need this inner function because we have two rounds of executions
        def _execute_steps(steps):
            # walk through steps
            for step in steps:
                try:
                    # are there any kwargs? If yes, pass them to the step.
                    if len(step) == 3:
                        if not self.run_step(step[0], step[1](), **step[2]):
                            return False
                    else:
                        if not self.run_step(step[0], step[1]()):
                            return False
                except StepNotFound, ex:
                    # OK, the step was not found, store and fail.
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

            # We got through all steps, everything seems to be ok.
            return True

        # We use this try block to make sure, we disconnect all connections.
        try:
            # Basic steps to prepare the test environment.
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
            # Execute the first round of steps
            result = _execute_steps(steps)
            # If any step failed, return the error.
            if not result:
                return result

            # Reset the step list
            steps = []

            # Every step from the config should be passed
            for step in self.config['build']:
                # We need to check for a explicit command, not none available
                # use the run_commands plugin.
                plugin = self.config['build_plugins'].get(step, None)

                # Get the real name of the step (including plugin)
                step_name = '%s[%s]' % (step, plugin) if plugin else step
                step_plugin = plugin or 'run_commands'

                # Append the step to the list of steps.
                steps.append(('execute step %s (%s)' % (step, step_plugin),
                    registry.get_step(plugin or 'run_commands'), {
                    'lines':self.config[step_name]}))

            # Execute the second round of steps.
            result = _execute_steps(steps)
            # Any errors? Return them!
            if not result:
                return result

        finally:
            # Disconnect server connections.
            disconnect_all()

        # If we reach this point, we're good.
        return True

    def run_step(self, name, task, **kwargs):
        # Every step has a start and finish time.
        step_starttime = datetime.now()

        # We need some IO to redirect stdout and stderr
        stdout = StringIO()
        stderr = StringIO()
        sys.stdout = stdout
        sys.stderr = stderr

        try:
            # Run the actual step.
            output, return_code = task(self, **kwargs)
            result = (output, None)
        except (SystemExit, Exception), ex:
            # We catch everything and report back to the backend.
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            exc =  ''.join(traceback.format_tb(exceptionTraceback))
            exc += ' '.join((str(exceptionType), str(exceptionValue)))

            output, return_code = '', 1
            result = (False, exc)
        finally:
            # After all, restore the stdout and stderr IO
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

        # Store the build step result.
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

        # Return the simplified result
        return result[0]
