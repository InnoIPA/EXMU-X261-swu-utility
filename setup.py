# Copyright (c) 2023 Innodisk Crop.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from setuptools import setup

setup(
    name="swu-utility",
    version="0.0.3",
    description="OTA toolings around EXMU-X261",
    install_requires=["paho-mqtt==1.5.1"],
    package_dir={"": "src"},
    packages=["swu_utility", "swu_utility.config"],
    package_data={"swu_utility.config": ["*.ini"]},
    entry_points={
        "console_scripts": [
            "swu-pusher = swu_utility.swu_pusher:main",
            "swu-scanner = swu_utility.swu_scanner:main",
            "swu-client = swu_utility.swu_client:main",
        ]
    },
)
