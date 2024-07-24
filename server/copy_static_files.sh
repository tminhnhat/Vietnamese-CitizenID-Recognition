#!/bin/bash
#cleanup

echo CLEANUP..
git reset --hard
echo COLLECT STATIC..
source ../../env/bin/activate
python3 manage.py collectstatic --noinput
deactivate
cd ..
sudo chown ubuntu:www-data . -R
sudo chmod +x . -R
sudo service idcard restart
echo DONE
