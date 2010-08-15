from celery.task import Task
from celery.registry import tasks

class BuildTask(Task):
    default_retry_delay = 10
    max_retries = 5

    def run(self, build_id, **kwargs):
        # Get a logger.
        logger = self.get_logger(**kwargs)
        # Catch everything and try again.
        try:
            # Load needed modules.
            from journeyman.buildrunner import BuildRunner
            from journeyman.builds.models import Build

            # Try to get the build.
            build = Build.objects.get(pk=build_id)

            # Create the build runner and start.
            build_runner = BuildRunner(build)
            build_runner.run_build()

            return True
        except Exception, exc:
            # Something went wrong. Retry.
            self.retry([build_id,], kwargs, exc=exc)

# Register with celery.
tasks.register(BuildTask)