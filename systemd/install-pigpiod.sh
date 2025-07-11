#!/usr/bin/env bash

if [ -d "pigpio" ]; then
    rm -rf pigpio

git clone https://github.com/joan2937/pigpio.git
cd pigpio

patch -p1 < ../pi5.patch

make
sudo make install

cd ..
sudo cp pigpiod.service /etc/systemd/system/pigpiod.service
sudo systemctl daemon-reload
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl status pigpiod
