#!/bin/bash

_dir="${1:-${PWD}}"
_user="${USER}"
_service="
[Unit]
Description=PixelPanel Service
After=network.target network-online.target
[Service]
User=root
ExecStart=${_dir}/start_server.sh
Restart=on-failure
[Install]
WantedBy=multi-user.target
"
_file="/lib/systemd/system/pixelpanel.service" 

echo "Creating PixelPanel service"
if [ -f "${_file}" ]; 
then
    echo "Erasing old service file"
    sudo rm "${_file}"
fi

sudo touch "${_file}"
sudo echo "${_service}" | sudo tee -a "${_file}" > /dev/null

echo "Enabling PixelPanel service to run on startup"
sudo systemctl daemon-reload
sudo systemctl enable pixelpanel.service
if [ $? != 0 ];
then
    echo "Error enabling PixelPanel service"
    exit 1
fi
sudo systemctl restart pixelpanel.service
echo "PixelPanel service enabled"
echo "Use sudo journalctl -u pixelpanel.service -f to see the logs"
exit 0
