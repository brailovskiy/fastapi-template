from app.celery_app.celery_executor import CeleryTasksExecutor


def get_celery_tasks_executor() -> CeleryTasksExecutor:
    return CeleryTasksExecutor()
