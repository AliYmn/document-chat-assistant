#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CELERY_PDF_QUEUE_NAME=${PDF_QUEUE_NAME}
export CELERY_PDF_WORKER_NAME=${PDF_WORKER_NAME}

celery -A pdf_service.core.worker.tasks.celery_app worker --loglevel=ERROR -E --queues=${CELERY_PDF_QUEUE_NAME} -n ${CELERY_PDF_WORKER_NAME}@%n
