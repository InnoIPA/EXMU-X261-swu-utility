#!/bin/bash
# Copyright (c) 2024 innodisk Crop.
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

DNA=${1}
SWU_FILE=${2}

### Scan all avalible devices.
if [ -z "$DNA" ] || [ ! -f "${SWU_FILE}" ]
then
    python3 src/swu_utility/swu_scanner.py -f src/swu_utility/config/config.ini
    exit
fi

### Update SWU to specific device.
python3 src/swu_utility/swu_pusher.py -d "${DNA}" -f src/swu_utility/config/config.ini "${SWU_FILE}"