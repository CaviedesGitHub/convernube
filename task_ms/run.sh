export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

sudo ufw allow 5002
gunicorn --bind 0.0.0.0:5002 wsgi:app