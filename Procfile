release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn xmen_agileteam.wsgi --log-file -