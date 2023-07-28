# OTA(swu client/pusher) for EXMU-X261

This repo provides an OTA solution for EXMU-X261. To perform OTA
updates, you need

1. an EXMU-X261 running `swu-client` service. (Use `sudo systemctl status swu-client` to verify that `swu-client.service` is active.)
2. mqtt broker and file server (Go to  [docker directory](https://github.com/InnoIPA/EXMU-X261-swu-utility/tree/main/docker) for more information)
3. a development machine with `swu-pusher` installed (See below)

# OTA User Guide

- [user guide](https://github.com/InnoIPA/EXMU-X261-usermanual/blob/ota/tocs/2.Software/OTA.md)
# How to install `swu-pusher`

To install `swu-pusher` on your development machine, execute

```
git clone https://github.com/InnoIPA/EXMU-X261-swu-utility
```
```
cd EXMU-X261-swu-utility
pip3 install ./
```

`swu-pusher` should be installed to `~/.local/bin/`. To verify it is available on your system, run

```
which swu-pusher
```

# `swu-client` RPM package

- [creating a RPM package](./docs/rpm.md)

# Configuration file

By default, `swu-client` and `swu-pusher` will connect to MQTT broker at `172.16.92.106`. You can change the setting by specifying a configuration file using `-f` option. We provide some [examples](https://github.com/InnoIPA/EXMU-X261-swu-utility/tree/main/src/swu_utility/config) of configuration file in the repo.

- default setting
    ```
    [broker]
    host = 172.16.92.106
    port = 1883

    [file server]
    host = 172.16.92.106
    port = 8080
    ```


# Command Line Arguments
```
usage: swu-pusher [-h] [-d DNA] [-m {AB,QSPI,RPM}] [-f CONFIG] image

positional arguments:
  image                 path to image file

optional arguments:
  -h, --help            show this help message and exit
  -d DNA, --dna DNA     DNA of target device
  -m {AB,QSPI,RPM}, --mode {AB,QSPI,RPM}
  -f CONFIG, --file CONFIG
                        path to config file
```

# Performance

| device |  rootfs size | boot part size | time spent |
|:------:|:------------:|:--------------:|:----------:|
|  eMMC  |    1.4GiB    |     100MiB     |    147s    |
|SD card |    1.4GiB    |     100MiB     |    116s    |
|QSPI fw |       x      |       x        |    10s     |

**Note:** We only measure the time spent on doing the update.
The time spent on downloads is ignored.
