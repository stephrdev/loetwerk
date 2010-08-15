from celery.task import Task
from celery.registry import tasks

class BuildTask(Task):
    default_retry_delay = 10
    max_retries = 5

    def run(self, build_id, **kwargs):
        logger = self.get_logger(**kwargs)
        try:
            from journeyman.buildrunner import BuildRunner
            from journeyman.builds.models import Build
            build = Build.objects.get(pk=build_id)
            logger.info('[%s] - running build..' % build)
            build_runner = BuildRunner(build)
            build_runner.run_build()
            return True
        except Exception, exc:
            logger.info('[%s] build failed: %s:%s' % (build_id, exc.__class__.__name__, exc))
            self.retry([build_id,], kwargs, exc=exc)

tasks.register(BuildTask)