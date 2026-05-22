FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY workers/requirements.txt /tmp/worker-requirements.txt
COPY apps/api/requirements.txt /tmp/api-requirements.txt
RUN pip install --no-cache-dir -r /tmp/worker-requirements.txt -r /tmp/api-requirements.txt

COPY apps /app/apps
COPY workers /app/workers
COPY packages /app/packages

ENV PYTHONPATH=/app

CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info"]
