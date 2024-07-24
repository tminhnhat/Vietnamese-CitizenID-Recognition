#!/bin/bash
#cleanup

echo CLEANUP..
git reset --hard
git checkout .
git pull
cd ..
sudo chown ubuntu:www-data . -R
sudo chmod +x . -R
sudo service idcard restart
echo DONE
