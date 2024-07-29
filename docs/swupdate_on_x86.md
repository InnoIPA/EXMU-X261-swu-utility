<!--
 Copyright (c) 2024 innodisk Crop.
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

# Overview
This page shows how to install `swupdate` under ubuntu.

- Default `swupdate` of ubuntu can install from `apt` is build with signed option, so building customised `swupdate` is in need.

# Requirement
```bash
sudo apt install -y libjson-c-dev liblua5.3-dev libubootenv-dev libconfig-dev libssl-dev libarchive-dev
```
# Build
1. Download source code.
    ```bash
    git clone https://github.com/sbabic/swupdate.git
    cd swupdate
    git checkout 0afeee8a2b0b2f2f7abd00deb93124804850e06d 
    ```
2. Copy the customised build config `.config` from [here](swu.config).
3. Build & install.
    ```bash
    make
    sudo make install
    ```