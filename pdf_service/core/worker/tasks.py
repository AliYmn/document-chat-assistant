from pdf_service.core.worker.config import celery_app


@celery_app.task(bind=True, name="test", max_retries=3, default_retry_delay=60)
def test(self) -> None:
    pass
