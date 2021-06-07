#!/bin/bash

if [ $(curl --silent --show-error http://localhost:4040/api/tunnels | sed -nE 's/.*public_url":"https:..([^\"]*).*/\1/p') ]
then
echo "Ngrok already running ..."
exit 1
else
echo "Ngrok not running, launch ngrok ..."
fi

nohup npx ngrok http 5005 > /tmp/nohup.out 2>&1 & 

until [ $(curl -s -o /dev/null -w "%{http_code}" http://localhost:4040/api/tunnels) == 200 ]
do
echo "Waiting for ngrok to start ..."
sleep 1s
done
until [ $(curl --silent --show-error http://localhost:4040/api/tunnels | sed -nE 's/.*public_url":"https:..([^\"]*).*/\1/p') ]
do
echo "Waiting for ngrok tunnel to be created ..."
sleep 1
done
