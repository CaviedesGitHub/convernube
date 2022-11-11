export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

sudo ufw allow 5003
gunicorn --bind 0.0.0.0:5003 wsgi:flask_app

#celery -A app.celery_app beat
#celery -A app.celery_app worker -l info --pool=solo
