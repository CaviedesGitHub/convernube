export FLASK_APP=app.py
export FLASK_DEBUG=1
export FLASK_ENV=development

sudo ufw allow 5001
gunicorn --bind 0.0.0.0:5001 wsgi:app

