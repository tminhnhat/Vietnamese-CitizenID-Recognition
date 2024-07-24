#!/bin/bash
echo COPY CONFIG..
sudo cp nginx_config/uwsgi/idcard.service /etc/systemd/system/
sudo cp nginx_config/nginx/idcard.conf /etc/nginx/conf.d/
echo RESTART SERVICE
sudo systemctl restart idcard
sudo systemctl restart nginx