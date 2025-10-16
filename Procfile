release: python manage.py migrate && python manage.py collectstatic --noinput && python create_admin_user.py
web: gunicorn xmen_agileteam.wsgi --log-file -