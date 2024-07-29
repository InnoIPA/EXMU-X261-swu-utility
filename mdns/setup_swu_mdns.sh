#!/bin/bash
# Copyright (c) 2024 innodisk Crop.
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

sudo cp avahi-alias@.service /etc/systemd/system/avahi-alias@.service

sudo systemctl enable --now avahi-alias@swu-server.local.service

sudo systemctl status avahi-alias@swu-server.local.service