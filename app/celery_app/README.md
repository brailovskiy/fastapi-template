# Start Celery

## Start celery worker

### windows
$env:PYTHONPATH="."; python -m celery -A app.celery_app.celery_app:celery worker --loglevel=debug -P solo

### linux/mac/unix 
PYTHONPATH=. celery -A app.celery_app.celery_app:celery worker --loglevel=info -c 4

## Start celery beat

### windows
$env:PYTHONPATH="."; python -m celery -A app.celery_app.celery_app:celery beat -l info

### linux/mac/unix 
PYTHONPATH=. celery -A app.celery_app.celery_app:celery beat -l info
