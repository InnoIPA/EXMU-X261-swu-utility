#!/bin/bash
# Copyright (c) 2024 innodisk Crop.
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

sudo rm -f /usr/local/bin/avahi-alias /etc/systemd/system/avahi-alias-swu.service

sudo systemctl daemon-reload