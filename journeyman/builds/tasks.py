from celery.task import Task
from celery.registry import tasks

from datetime import datetime

class BuildTask(Task):
    default_retry_delay = 10
    max_retries = 2

    def run(self, build_id, **kwargs):
        # Get a logger.
        logger = self.get_logger(**kwargs)
        # Catch everything and try again.
        try:
            # Load needed modules.
            from journeyman.buildrunner import BuildRunner
            from journeyman.builds.models import Build, BuildState

            # Try to get the build.
            build = Build.objects.get(pk=build_id)

            # Create the build runner and start.
            build_runner = BuildRunner(build)
            build_runner.run_build()

            return True
        except Exception, exc:
            build = Build.objects.get(pk=build_id)
            build.state = BuildState.FAILED
            build.finished = datetime.now()
            build.save()

# Register with celery.
tasks.register(BuildTask)