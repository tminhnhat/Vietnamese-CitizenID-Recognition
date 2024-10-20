#!/bin/bash
# python3.8 manage.py crontab remove
# python3.8 manage.py crontab add

# systemctl restart crond.service


python3 manage.py runserver --insecure 0.0.0.0:80 &
