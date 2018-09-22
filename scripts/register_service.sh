#!/usr/bin/env bash

# copy service file into /lib/systemd/system/guin.service
sudo systemctl stop guin.service
sudo cp -f guin.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable guin.service

sudo systemctl start guin.service
sudo systemctl status guin.service
