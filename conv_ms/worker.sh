celery -A app.celery_app beat
celery -A app.celery_app worker -l info --pool=solo