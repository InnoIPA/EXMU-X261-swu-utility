# Copyright (c) 2023 Innodisk Crop.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import json
import configparser
import subprocess
from enum import IntEnum
from os.path import basename
from argparse import ArgumentParser
import importlib.resources as res

from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import connack_string

import swu_utility.config as config


# https://github.com/sbabic/swupdate/blob/d542b7fa7c8b7ddb75e7cb3335f5a2590df2edab/include/swupdate_status.h#L21-L31
class TelemetryStatus(IntEnum):
    IDLE, START, RUN, SUCCESS, FAILURE, DOWNLOAD, DONE, SUBPROCESS, PROGRESS = range(9)


class Pusher(MQTTClient):
    def __init__(self, dna, url, mode):
        super().__init__()
        self.dna = dna
        self.url = url
        self.mode = mode
        self.package_topic = f"v0/EXMU-X261/ota/package/{self.dna}"
        self.telemetry_topic = f"v0/EXMU-X261/ota/telemetry/{self.dna}"

    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT connection returned result: {connack_string(rc)}")

        p = {"url": self.url, "mode": self.mode}
        self.publish(self.package_topic, payload=json.dumps(p))
        self.subscribe(self.telemetry_topic)

    def on_message(self, client, userdata, message):
        if message.topic == self.telemetry_topic:
            m = json.loads(message.payload)
            status = m["status"]
            cur_percent = m["cur_percent"]
            dwl_percent = m["dwl_percent"]
            cur_image = m["cur_image"]

            if status == TelemetryStatus.DOWNLOAD:
                print(f"[DOWNLOAD] {cur_image}: {dwl_percent}%", end="\r")
                if dwl_percent == 100:
                    print()
            elif status == TelemetryStatus.PROGRESS:
                print(f"[INSTALL] {cur_image}: {cur_percent}%", end="\r")
                if cur_percent == 100:
                    print()
            else:
                print(f"[{TelemetryStatus(status).name}]")
                if status == TelemetryStatus.DONE or status == TelemetryStatus.FAILURE:
                    self.disconnect()
        else:
            print(
                (
                    f"Received message '{message.payload}' on topic '{message.topic}' "
                    f"with Qos {message.qos}"
                )
            )


def main():
    # Initialization
    parser = ArgumentParser()
    parser.add_argument("image", help="path to image file")
    parser.add_argument(
        "-d", "--dna", help="DNA of target device", dest="dna", default="dna"
    )
    parser.add_argument(
        "-m", "--mode", choices=["AB", "QSPI", "RPM"], dest="mode", default="AB"
    )
    parser.add_argument("-f", "--file", help="path to config file", dest="config")
    args = parser.parse_args()
    image = args.image

    if args.config:
        config_file = open(args.config)
    else:
        config_file = res.open_text(config, "config.ini")

    with config_file as c:
        opt = configparser.ConfigParser()
        opt.read_file(c)
        broker_host = opt["broker"]["host"]
        broker_port = opt["broker"].getint("port")
        base_url = f'{opt["file server"]["host"]}:{opt["file server"]["port"]}'

    # Upload image to http server
    p = subprocess.run(
        ["curl", "-F", f"path=@{image}", f"{base_url}/upload?path=/"],
        stdout=subprocess.PIPE,
        text=True,
    )
    if p.stdout:
        print(f"[ERROR] Failed to upload {image}")
        print(f"[INFO] {p.stdout}")
        # exit(1)
    if p.returncode != 0:
        print(f"[ERROR] Failed to upload {image}")
        print(f"curl commands: {p.args}")
        print(f"curl exit code: {p.returncode}")
        exit(1)

    # Connect to mqtt broker
    client = Pusher(args.dna, f"{base_url}/{basename(image)}", args.mode)
    client.connect(broker_host, broker_port)
    client.loop_forever()


if __name__ == "__main__":
    main()
