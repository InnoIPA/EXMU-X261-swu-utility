#!/bin/bash
# Copyright (c) 2024 innodisk Crop.
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

sudo apt install -y python3-avahi

sudo cp avahi-alias /usr/local/bin/avahi-alias

sudo cp avahi-alias-swu.service /etc/systemd/system/avahi-alias-swu.service

sudo systemctl enable avahi-alias-swu.service

sudo systemctl start avahi-alias-swu.service