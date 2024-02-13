#!/bin/bash
echo $1
if [ "$1" == "django" ]; then
    echo "Starting Django Server"
    /usr/local/bin/python /code/django/manage.py runserver 0.0.0.0:5000
elif [ "$1" == "worker" ]; then
    echo "Starting Worker Server"
    /usr/local/bin/python /code/worker/executor.py
elif [ "$1" == "open" ]; then
    echo "Starting Worker Server"
    /bin/bash
else
    echo "Server not specified, Exiting."
    exit 1
fi