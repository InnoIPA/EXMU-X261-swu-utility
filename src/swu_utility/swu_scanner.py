# Copyright (c) 2024 Innodisk Crop.
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import time
import configparser
from argparse import ArgumentParser
import importlib.resources as res

from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import connack_string

import swu_utility.config as config

class Scanner(MQTTClient):
    def __init__(self):
        super().__init__()
        self.dna_get_topic = f"v0/EXMU-X261/ota/dna/get"
        self.dna_post_topic = f"v0/EXMU-X261/ota/dna/post"

    def on_connect(self, client, userdata, flags, rc):
        print(f"MQTT connection returned result: {connack_string(rc)}")
        self.subscribe(self.dna_post_topic)
        self.publish(self.dna_get_topic)
        print(f"Scaning avalible DNA devices:")

    def on_message(self, client, userdata, message):
        if message.topic == self.dna_post_topic:
            print(message.payload.decode('utf-8'))


def main():
    # Initialization
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", help="path to config file", dest="config")
    args = parser.parse_args()

    if args.config:
        config_file = open(args.config)
    else:
        config_file = res.open_text(config, "config.ini")

    with config_file as c:
        opt = configparser.ConfigParser()
        opt.read_file(c)
        broker_host = opt["broker"]["host"]
        broker_port = opt["broker"].getint("port")

    # Connect to mqtt broker
    client = Scanner()
    client.connect(broker_host, broker_port)

    # Scan avalible dna for 5 second.
    client.loop_start()
    time.sleep(5)
    client.loop_stop()

if __name__ == "__main__":
    main()
