#!/usr/bin/env bash

git clone https://github.com/joan2937/pigpio.git
cd pigpio
make
sudo make install

cd ..
sudo cp pigpiod.service /etc/systemd/system/pigpiod.service
sudo systemctl daemon-reload
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl status pigpiod
