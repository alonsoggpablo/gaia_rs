#!/bin/sh


# until cd /gaia_rs
# do
#     echo "Waiting for server volume..."
# done


# until python manage.py migrate
# do
#     echo "Waiting for db to be ready..."
#     sleep 2
# done


# python manage.py collectstatic --noinput

# python manage.py createsuperuser --noinput

gunicorn gaia_rs.wsgi --bind 0.0.0.0:8000 --workers 4 --threads 4

# for debug
#python manage.py runserver 0.0.0.0:8000